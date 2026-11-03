"""
Test Suite: ExamOps Demo Authentication Security & RBAC Invariants
Verifies:
1. Demo login disabled returns 403.
2. Missing or incorrect demo access key returns 403.
3. All four allowed roles receive only their own role.
4. Platform Administrator demo login is rejected.
5. Tampering with the requested role cannot grant additional privileges.
6. Backend authorization rejects unauthorized operations.
7. Production startup fails with an unsafe JWT secret.
"""
import pytest
import uuid
import base64
import json
from jose import jwt
from fastapi.testclient import TestClient
from backend.main import app, lifespan
from backend.config import Settings, settings, validate_security_configuration, DEFAULT_DEV_JWT_SECRET
from backend.database import execute_query, execute_mutation
from backend.auth import create_access_token, verify_and_decode_jwt, _profile_cache

client = TestClient(app)

TEST_DEMO_KEY = "examops-secure-evaluation-key-20261022-strong"

# ==============================================================================
# 1. DEMO LOGIN DISABLED RETURNS 403
# ==============================================================================

def test_demo_login_disabled_returns_403(monkeypatch):
    """When DEMO_LOGIN_ENABLED is False, demo-login and demo-roles must return HTTP 403."""
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", False)
    monkeypatch.setattr(settings, "DEMO_ACCESS_KEY", TEST_DEMO_KEY)

    # 1. POST /api/auth/demo-login
    res = client.post(
        "/api/auth/demo-login",
        json={"role": "ACADEMIC_ADMINISTRATOR"},
        headers={"X-Demo-Access-Key": TEST_DEMO_KEY},
    )
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
    assert "disabled" in res.json().get("detail", "").lower()

    # 2. GET /api/auth/demo-roles
    res_roles = client.get("/api/auth/demo-roles")
    assert res_roles.status_code == 403
    assert "disabled" in res_roles.json().get("detail", "").lower()


# ==============================================================================
# 2. KEYLESS DEMO LOGIN & RATE LIMITING
# ==============================================================================

def test_demo_login_rate_limiting(monkeypatch):
    """Verify rate limiter blocks client when exceeding 30 requests per window."""
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", True)
    from backend.routes.auth_routes import _demo_rate_limiter
    _demo_rate_limiter.reset()

    # Fill up 30 allowed requests
    for _ in range(30):
        res = client.post("/api/auth/demo-login", json={"role": "LEARNER"})
        assert res.status_code == 200

    # 31st request must trigger HTTP 429
    res_limited = client.post("/api/auth/demo-login", json={"role": "LEARNER"})
    assert res_limited.status_code == 429
    assert "rate limit exceeded" in res_limited.json().get("detail", "").lower()
    _demo_rate_limiter.reset()


def test_missing_and_inactive_profiles_rejected(monkeypatch):
    """Verify demo login rejects unsupported roles and missing accounts."""
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", True)
    from backend.routes.auth_routes import _demo_rate_limiter
    _demo_rate_limiter.reset()

    # Case A: Unsupported role
    res_unsupported = client.post(
        "/api/auth/demo-login",
        json={"role": "UNKNOWN_ROLE"},
    )
    assert res_unsupported.status_code == 403
    assert "Unsupported demo role" in res_unsupported.json().get("detail", "")

    # Case B: Inactive profile query
    res_inactive = client.post(
        "/api/auth/demo-login",
        json={"role": "STUDENT_INACTIVE_MOCK"},
    )
    assert res_inactive.status_code == 403


# ==============================================================================
# 3. ALL FOUR ALLOWED ROLES RECEIVE ONLY THEIR OWN ROLE (PASSWORDLESS)
# ==============================================================================

@pytest.mark.parametrize("requested_role", [
    "ACADEMIC_ADMINISTRATOR",
    "INSTRUCTOR",
    "SUPPORT_STAFF",
    "LEARNER",
])
def test_all_four_allowed_roles_receive_only_their_own_role(monkeypatch, requested_role):
    """Verify each of the 4 allowed demo roles receives exclusively their own authoritative role without any access key."""
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", True)
    from backend.routes.auth_routes import _demo_rate_limiter
    _demo_rate_limiter.reset()

    res = client.post(
        "/api/auth/demo-login",
        json={"role": requested_role},
    )
    assert res.status_code == 200, f"Failed for role {requested_role}: {res.text}"
    data = res.json()

    # 1. Inspect response envelope
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["demo_mode"] is True
    user = data["user"]
    assert user["role"] == requested_role

    # 2. Authenticate against /api/auth/me using the issued token
    token = data["access_token"]
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["role"] == requested_role
    assert me_data["id"] == user["id"]
    assert me_data["email"] == user["email"]


# ==============================================================================
# 4. PLATFORM ADMINISTRATOR DEMO LOGIN IS REJECTED
# ==============================================================================

def test_platform_administrator_demo_login_rejected(monkeypatch):
    """PLATFORM_ADMINISTRATOR and SUPER_ADMIN roles are strictly prohibited via demo login."""
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", True)
    from backend.routes.auth_routes import _demo_rate_limiter
    _demo_rate_limiter.reset()

    # 1. Attempt PLATFORM_ADMINISTRATOR
    res_platform = client.post(
        "/api/auth/demo-login",
        json={"role": "PLATFORM_ADMINISTRATOR"},
    )
    assert res_platform.status_code == 403
    assert "Platform Administrator" in res_platform.json().get("detail", "")

    # 2. Attempt SUPER_ADMIN alias
    res_super = client.post(
        "/api/auth/demo-login",
        json={"role": "SUPER_ADMIN"},
    )
    assert res_super.status_code == 403

    # 3. Check /api/auth/demo-roles does not advertise PLATFORM_ADMINISTRATOR
    res_roles = client.get("/api/auth/demo-roles")
    assert res_roles.status_code == 200
    available_role_ids = [r["id"] for r in res_roles.json()]
    assert "PLATFORM_ADMINISTRATOR" not in available_role_ids
    assert "SUPER_ADMIN" not in available_role_ids
    assert set(available_role_ids) == {"ACADEMIC_ADMINISTRATOR", "INSTRUCTOR", "SUPPORT_STAFF", "LEARNER"}


# ==============================================================================
# 5. TAMPERING WITH REQUESTED ROLE CANNOT GRANT ADDITIONAL PRIVILEGES
# ==============================================================================

def test_tampering_with_requested_role_cannot_grant_additional_privileges(monkeypatch):
    """Arbitrary role strings, injection attempts, and client header spoofing cannot elevate privileges."""
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", True)
    from backend.routes.auth_routes import _demo_rate_limiter
    _demo_rate_limiter.reset()

    # Case A: Unsupported arbitrary roles
    for arbitrary_role in ["ROOT", "SYSADMIN", "AUDITOR", "DB_ADMIN", "DEVELOPER"]:
        res = client.post(
            "/api/auth/demo-login",
            json={"role": arbitrary_role},
        )
        assert res.status_code == 403

    # Case B: SQL injection payload in role parameter
    res_inject = client.post(
        "/api/auth/demo-login",
        json={"role": "' OR '1'='1' --"},
    )
    assert res_inject.status_code == 403

    # Case C: Obtain legitimate LEARNER token, then send spoofing headers (e.g. X-Test-Role)
    learner_login = client.post(
        "/api/auth/demo-login",
        json={"role": "LEARNER"},
    )
    assert learner_login.status_code == 200
    learner_token = learner_login.json()["access_token"]

    # Tampering header: Attempting to claim PLATFORM_ADMINISTRATOR while bearing LEARNER token
    tampered_me = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {learner_token}",
            "X-Test-Role": "PLATFORM_ADMINISTRATOR",
        },
    )
    assert tampered_me.status_code == 200
    # Resolved user MUST remain LEARNER because PostgreSQL profile is authoritative
    assert tampered_me.json()["role"] == "LEARNER"


# ==============================================================================
# 6. BACKEND AUTHORIZATION REJECTS UNAUTHORIZED OPERATIONS
# ==============================================================================

def test_backend_authorization_rejects_unauthorized_operations(monkeypatch):
    """Verify backend RBAC strictly forbids unauthorized operations across issued tokens."""
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", True)
    from backend.routes.auth_routes import _demo_rate_limiter
    _demo_rate_limiter.reset()

    # 1. Learner Token Constraints
    learner_res = client.post(
        "/api/auth/demo-login",
        json={"role": "LEARNER"},
    )
    learner_token = learner_res.json()["access_token"]
    learner_headers = {"Authorization": f"Bearer {learner_token}"}

    # Learner cannot view user profiles
    assert client.get("/api/auth/profiles", headers=learner_headers).status_code == 403
    # Learner cannot initiate scheduling runs
    assert client.post("/api/scheduling/runs", json={}, headers=learner_headers).status_code == 403
    # Learner cannot inspect system audit logs
    assert client.get("/api/audit/logs", headers=learner_headers).status_code == 403

    # 2. Instructor Token Constraints
    inst_res = client.post(
        "/api/auth/demo-login",
        json={"role": "INSTRUCTOR"},
    )
    inst_token = inst_res.json()["access_token"]
    inst_headers = {"Authorization": f"Bearer {inst_token}"}

    # Instructor cannot initiate scheduling runs
    assert client.post("/api/scheduling/runs", json={}, headers=inst_headers).status_code == 403
    # Instructor cannot mutate user profiles
    dummy_uuid = str(uuid.uuid4())
    assert client.patch(f"/api/auth/profiles/{dummy_uuid}", json={"display_name": "Hack"}, headers=inst_headers).status_code == 403

    # 3. Support Staff Token Constraints
    staff_res = client.post(
        "/api/auth/demo-login",
        json={"role": "SUPPORT_STAFF"},
    )
    staff_token = staff_res.json()["access_token"]
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # Support Staff cannot initiate scheduling runs
    assert client.post("/api/scheduling/runs", json={}, headers=staff_headers).status_code == 403
    # Support Staff cannot mutate user profiles
    assert client.patch(f"/api/auth/profiles/{dummy_uuid}", json={"display_name": "Hack"}, headers=staff_headers).status_code == 403

    # 4. Academic Administrator Token Constraints
    admin_res = client.post(
        "/api/auth/demo-login",
        json={"role": "ACADEMIC_ADMINISTRATOR"},
    )
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Academic Administrator CAN view profiles (Read only)
    assert client.get("/api/auth/profiles?limit=2", headers=admin_headers).status_code == 200
    # Academic Administrator CANNOT mutate profiles (Platform Administrator only)
    assert client.patch(f"/api/auth/profiles/{dummy_uuid}", json={"display_name": "Hack"}, headers=admin_headers).status_code == 403


# ==============================================================================
# 7. PRODUCTION STARTUP FAILS WITH AN UNSAFE JWT SECRET
# ==============================================================================

def test_production_startup_fails_with_unsafe_jwt_secret():
    """Verify application configuration validation blocks startup in production with insecure secrets."""
    # Case A: Default development JWT secret in production
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY=DEFAULT_DEV_JWT_SECRET,
        )
    assert "Unsafe JWT_SECRET_KEY detected in production" in str(exc_info.value)

    # Case B: Short JWT secret (< 32 characters)
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY="short-secret-key-too-brief",
        )
    assert "Unsafe JWT_SECRET_KEY detected in production" in str(exc_info.value)

    # Case C: Empty JWT secret
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY="",
        )
    assert "Unsafe JWT_SECRET_KEY detected in production" in str(exc_info.value)

    # Case D: Secret containing "dev-secret" keyword
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY="my-custom-dev-secret-string-that-is-long-enough-32-chars",
        )
    assert "Unsafe JWT_SECRET_KEY detected in production" in str(exc_info.value)

    # Case E: Valid strong production configuration succeeds
    valid_prod_settings = Settings(
        ENVIRONMENT="production",
        JWT_SECRET_KEY="b" * 64,
        DEMO_LOGIN_ENABLED=False,
    )
    assert valid_prod_settings.ENVIRONMENT == "production"
    assert len(valid_prod_settings.JWT_SECRET_KEY) == 64


# ==============================================================================
# 8. DEV SWITCH ROLE ENVIRONMENT VALIDATION
# ==============================================================================

@pytest.mark.parametrize("prod_env", [
    "production",
    "prod",
    "Production",
    "PROD",
    " PRODUCTION ",
    "  prod  ",
])
def test_dev_switch_role_forbidden_in_production(monkeypatch, prod_env):
    """Verify /dev-switch-role is strictly forbidden (HTTP 403) across all production environment variations."""
    monkeypatch.setattr(settings, "ENVIRONMENT", prod_env)
    res = client.post("/api/auth/dev-switch-role", json={"role": "LEARNER"})
    assert res.status_code == 403
    assert "Role switching is disabled in production" in res.json().get("detail", "")

def test_dev_switch_role_allowed_in_development(monkeypatch):
    """Verify /dev-switch-role remains functional in non-production environments."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    res = client.post("/api/auth/dev-switch-role", json={"role": "LEARNER"})
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "LEARNER"


# ==============================================================================
# 9. JWT SIGNATURE, EXPIRATION & KEY SECURITY
# ==============================================================================

def test_invalid_signature_rejection():
    """Verify that a Bearer token with a tampered or invalid cryptographic signature is rejected with HTTP 401."""
    valid_token = create_access_token(
        user_id="d082c415-67b4-5c33-bc25-62e65c25241a",
        email="exam.director.1@examops.institution.edu",
        role="ACADEMIC_ADMINISTRATOR",
    )
    parts = valid_token.split(".")
    assert len(parts) == 3
    # Corrupt the signature component
    corrupted_token = f"{parts[0]}.{parts[1]}.invalid_signature_{parts[2][:6]}"

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {corrupted_token}"})
    assert res.status_code == 401
    assert "Invalid or expired Bearer token signature" in res.json().get("detail", "")


def test_expired_token_rejection():
    """Verify that an expired Bearer token is rejected with HTTP 401."""
    expired_token = create_access_token(
        user_id="d082c415-67b4-5c33-bc25-62e65c25241a",
        email="exam.director.1@examops.institution.edu",
        role="ACADEMIC_ADMINISTRATOR",
        expires_delta_seconds=-3600,
    )
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert "Invalid or expired Bearer token signature" in res.json().get("detail", "")


def test_unknown_signing_key_rejection():
    """Verify that tokens signed with unknown secrets or unknown JWKS key IDs are rejected with HTTP 401."""
    # Subcase A: HS256 signed with unknown HMAC secret
    foreign_token = jwt.encode(
        {"sub": "d082c415-67b4-5c33-bc25-62e65c25241a", "email": "test@unknown.com", "role": "LEARNER", "exp": 9999999999},
        "foreign-untrusted-secret-key-32chars-min!",
        algorithm="HS256",
    )
    res_a = client.get("/api/auth/me", headers={"Authorization": f"Bearer {foreign_token}"})
    assert res_a.status_code == 401
    assert "Invalid or expired Bearer token signature" in res_a.json().get("detail", "")

    # Subcase B: Asymmetric token with unknown kid and dummy payload
    header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "kid": "unknown-nonexistent-key-id-999"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": "d082c415-67b4-5c33-bc25-62e65c25241a", "exp": 9999999999}).encode()).decode().rstrip("=")
    dummy_rs256_token = f"{header}.{payload}.dummysignature"
    res_b = client.get("/api/auth/me", headers={"Authorization": f"Bearer {dummy_rs256_token}"})
    assert res_b.status_code == 401
    assert "Invalid or expired Bearer token signature" in res_b.json().get("detail", "")


# ==============================================================================
# 10. ENVIRONMENT-SCORED TEST HEADER SECURITY
# ==============================================================================

@pytest.mark.parametrize("prod_env", [
    "production",
    "prod",
    "Production",
    "PROD",
    " PRODUCTION ",
    "  prod  ",
])
def test_all_production_environment_variants_block_test_headers(monkeypatch, prod_env):
    """Verify that all production environment variations strictly block X-Test-* bypass headers."""
    monkeypatch.setattr(settings, "ENVIRONMENT", prod_env)
    _profile_cache.clear()

    # Case A: X-Test-Role attempt
    res_role = client.get("/api/auth/me", headers={"X-Test-Role": "ACADEMIC_ADMINISTRATOR"})
    assert res_role.status_code == 401
    assert "Authentication required. Provide a valid Bearer token." in res_role.json().get("detail", "")

    # Case B: X-Test-User-Id attempt
    res_uid = client.get("/api/auth/me", headers={"X-Test-User-Id": "d082c415-67b4-5c33-bc25-62e65c25241a"})
    assert res_uid.status_code == 401
    assert "Authentication required. Provide a valid Bearer token." in res_uid.json().get("detail", "")


@pytest.mark.parametrize("dev_env", [
    "development",
    "test",
    "local",
    "staging",
])
def test_development_and_test_environments_retain_test_headers(monkeypatch, dev_env):
    """Verify that development and non-production environments retain the intended test-header behavior."""
    monkeypatch.setattr(settings, "ENVIRONMENT", dev_env)
    _profile_cache.clear()

    # Case A: X-Test-Role resolves to an active profile of that role
    res_role = client.get("/api/auth/me", headers={"X-Test-Role": "ACADEMIC_ADMINISTRATOR"})
    assert res_role.status_code == 200
    assert res_role.json()["role"] == "ACADEMIC_ADMINISTRATOR"

    # Case B: X-Test-User-Id resolves the specific user
    user_id = res_role.json()["id"]
    res_uid = client.get("/api/auth/me", headers={"X-Test-User-Id": user_id})
    assert res_uid.status_code == 200
    assert res_uid.json()["id"] == user_id


# ==============================================================================
# 11. INACTIVE ACCOUNT REJECTION
# ==============================================================================

def test_inactive_account_rejection():
    """Verify that accounts marked INACTIVE or suspended are rejected with HTTP 401 even with a valid token."""
    test_inactive_id = str(uuid.uuid4())
    test_email = f"inactive_{test_inactive_id[:8]}@examops.test"
    try:
        execute_mutation(
            """
            INSERT INTO user_profiles (id, email, display_name, role, status)
            VALUES (%s, %s, %s, %s, 'INACTIVE');
            """,
            (test_inactive_id, test_email, "Inactive Tester", "LEARNER"),
        )
        _profile_cache.clear()

        # Generate a valid token with matching user ID
        token = create_access_token(
            user_id=test_inactive_id,
            email=test_email,
            role="LEARNER",
        )

        res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 401
        detail = res.json().get("detail", "")
        assert "inactive or suspended" in detail.lower()
        assert test_email in detail
    finally:
        execute_mutation("DELETE FROM user_profiles WHERE id = %s;", (test_inactive_id,))
        _profile_cache.clear()


# ==============================================================================
# 12. SUPABASE_JWT_SECRET & HS256 SECURITY INVARIANTS
# ==============================================================================

def test_weak_configured_supabase_jwt_secret_rejected_in_production():
    """Verify production startup rejects weak, short, or default SUPABASE_JWT_SECRET without leaking secret values."""
    # Case A: Short secret (< 32 characters)
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY="a" * 64,
            SUPABASE_JWT_SECRET="short-secret-value",
        )
    err = str(exc_info.value)
    assert "Unsafe SUPABASE_JWT_SECRET detected in production" in err
    assert "short-secret-value" not in err  # Must never leak secret

    # Case B: Empty string configured
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY="a" * 64,
            SUPABASE_JWT_SECRET="",
        )
    assert "Unsafe SUPABASE_JWT_SECRET detected in production" in str(exc_info.value)

    # Case C: Whitespace-only string configured
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY="a" * 64,
            SUPABASE_JWT_SECRET="    ",
        )
    assert "Unsafe SUPABASE_JWT_SECRET detected in production" in str(exc_info.value)

    # Case D: Known weak password
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY="a" * 64,
            SUPABASE_JWT_SECRET="secret",
        )
    assert "Unsafe SUPABASE_JWT_SECRET detected in production" in str(exc_info.value)

    # Case E: Genuinely unset SUPABASE_JWT_SECRET succeeds in production
    valid_prod = Settings(
        ENVIRONMENT="production",
        JWT_SECRET_KEY="a" * 64,
        SUPABASE_JWT_SECRET=None,
    )
    assert valid_prod.SUPABASE_JWT_SECRET is None


@pytest.mark.parametrize("placeholder_variant", [
    "placeholder" + "x" * 32,
    "PLACEHOLDER" + "x" * 32,
    "x" * 20 + "placeholder" + "y" * 20,
    "x" * 20 + "PlAcEhOlDeR" + "y" * 20,
])
def test_placeholder_secrets_rejected_regardless_of_capitalization_or_position(placeholder_variant):
    """Verify placeholder secrets are rejected at startup and runtime regardless of casing or position."""
    # 1. Startup validation in production rejects placeholder
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY="a" * 64,
            SUPABASE_JWT_SECRET=placeholder_variant,
        )
    assert "Unsafe SUPABASE_JWT_SECRET detected in production" in str(exc_info.value)
    assert placeholder_variant not in str(exc_info.value)

    # 2. Runtime verification in verify_and_decode_jwt skips placeholder secrets
    dummy_token = jwt.encode(
        {"sub": "d082c415-67b4-5c33-bc25-62e65c25241a", "exp": 9999999999},
        placeholder_variant,
        algorithm="HS256",
    )
    orig_supabase = settings.SUPABASE_JWT_SECRET
    try:
        settings.SUPABASE_JWT_SECRET = placeholder_variant
        assert verify_and_decode_jwt(dummy_token) is None
    finally:
        settings.SUPABASE_JWT_SECRET = orig_supabase


def test_both_distinct_valid_hs256_secrets_verified_correctly(monkeypatch):
    """Verify both distinct configured HS256 secrets (JWT_SECRET_KEY and SUPABASE_JWT_SECRET) decode correctly."""
    secret_main = "m" * 64
    secret_supabase = "s" * 64

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret_main)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret_supabase)
    _profile_cache.clear()

    user_id = "d082c415-67b4-5c33-bc25-62e65c25241a"
    email = "exam.director.1@examops.institution.edu"

    # Token A signed with JWT_SECRET_KEY
    token_main = jwt.encode(
        {"sub": user_id, "email": email, "role": "ACADEMIC_ADMINISTRATOR", "exp": 9999999999},
        secret_main,
        algorithm="HS256",
    )

    # Token B signed with SUPABASE_JWT_SECRET (must include exact Supabase issuer)
    expected_iss = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"
    token_supabase = jwt.encode(
        {"sub": user_id, "email": email, "role": "ACADEMIC_ADMINISTRATOR", "iss": expected_iss, "exp": 9999999999},
        secret_supabase,
        algorithm="HS256",
    )

    # Verify both decode via verify_and_decode_jwt
    payload_a = verify_and_decode_jwt(token_main)
    assert payload_a is not None
    assert payload_a["sub"] == user_id

    payload_b = verify_and_decode_jwt(token_supabase)
    assert payload_b is not None
    assert payload_b["sub"] == user_id

    # Verify both authenticate via /api/auth/me
    res_a = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_main}"})
    assert res_a.status_code == 200
    assert res_a.json()["id"] == user_id

    res_b = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_supabase}"})
    assert res_b.status_code == 200
    assert res_b.json()["id"] == user_id


def test_invalid_signatures_remain_rejected_with_dual_secrets(monkeypatch):
    """Verify invalid/corrupted signatures and foreign secrets are rejected when dual secrets are configured."""
    secret_main = "m" * 64
    secret_supabase = "s" * 64
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret_main)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret_supabase)
    _profile_cache.clear()

    user_id = "d082c415-67b4-5c33-bc25-62e65c25241a"

    # 1. Foreign secret token
    foreign_token = jwt.encode(
        {"sub": user_id, "exp": 9999999999},
        "foreign-secret-untrusted-key-at-least-32-chars!",
        algorithm="HS256",
    )
    res_foreign = client.get("/api/auth/me", headers={"Authorization": f"Bearer {foreign_token}"})
    assert res_foreign.status_code == 401
    assert "Invalid or expired Bearer token signature" in res_foreign.json().get("detail", "")

    # 2. Corrupted signature on valid token
    valid_token = jwt.encode({"sub": user_id, "exp": 9999999999}, secret_main, algorithm="HS256")
    parts = valid_token.split(".")
    corrupted_token = f"{parts[0]}.{parts[1]}.bad_signature_12345"
    res_corrupt = client.get("/api/auth/me", headers={"Authorization": f"Bearer {corrupted_token}"})
    assert res_corrupt.status_code == 401


def test_existing_es256_rs256_verification_remains_unaffected(monkeypatch):
    """Verify asymmetric ES256/RS256 verification is strictly isolated and unaffected by HS256 secrets."""
    secret_main = "m" * 64
    secret_supabase = "s" * 64
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret_main)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret_supabase)

    # 1. RS256 token with unknown kid is rejected immediately in Step 1 without fallback
    header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "kid": "unknown-nonexistent-key"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": "d082c415-67b4-5c33-bc25-62e65c25241a", "exp": 9999999999}).encode()).decode().rstrip("=")
    token_rs256 = f"{header}.{payload}.dummy_signature"

    assert verify_and_decode_jwt(token_rs256) is None
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_rs256}"})
    assert res.status_code == 401

    # 2. Algorithm confusion test: An RS256-signed token cannot be accepted as HS256
    # and Step 2 will reject it because algorithms=['HS256'] enforces the header alg
    assert verify_and_decode_jwt(token_rs256) is None


# ==============================================================================
# 13. EXACT ISSUER VALIDATION & NO-FALLTHROUGH INVARIANTS
# ==============================================================================

def test_missing_issuer_rejected_for_supabase_tokens(monkeypatch):
    """Verify that Supabase tokens (both HS256 and ES256/RS256) lacking an 'iss' claim are rejected."""
    secret_main = "m" * 64
    secret_supabase = "s" * 64
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret_main)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret_supabase)
    _profile_cache.clear()

    user_id = "d082c415-67b4-5c33-bc25-62e65c25241a"

    # Case A: HS256 token signed with SUPABASE_JWT_SECRET missing 'iss' claim
    token_no_iss = jwt.encode(
        {"sub": user_id, "email": "test@examops.edu", "role": "LEARNER", "exp": 9999999999},
        secret_supabase,
        algorithm="HS256",
    )
    assert verify_and_decode_jwt(token_no_iss) is None
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_no_iss}"})
    assert res.status_code == 401

    # Case B: RS256 token missing 'iss' claim
    header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "kid": "any-kid"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": user_id, "exp": 9999999999}).encode()).decode().rstrip("=")
    token_rs256_no_iss = f"{header}.{payload}.dummy_signature"
    assert verify_and_decode_jwt(token_rs256_no_iss) is None


def test_incorrect_issuer_rejected_for_all_tokens(monkeypatch):
    """Verify that any token with an incorrect issuer is rejected and not accepted."""
    secret_main = "m" * 64
    secret_supabase = "s" * 64
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret_main)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret_supabase)
    _profile_cache.clear()

    user_id = "d082c415-67b4-5c33-bc25-62e65c25241a"
    bad_iss = "https://untrusted-foreign-project.supabase.co/auth/v1"

    # Case A: HS256 token signed with SUPABASE_JWT_SECRET with incorrect 'iss'
    token_bad_iss_supabase = jwt.encode(
        {"sub": user_id, "email": "test@examops.edu", "role": "LEARNER", "iss": bad_iss, "exp": 9999999999},
        secret_supabase,
        algorithm="HS256",
    )
    assert verify_and_decode_jwt(token_bad_iss_supabase) is None
    res_a = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_bad_iss_supabase}"})
    assert res_a.status_code == 401

    # Case B: HS256 token signed with JWT_SECRET_KEY with incorrect 'iss'
    token_bad_iss_main = jwt.encode(
        {"sub": user_id, "email": "test@examops.edu", "role": "LEARNER", "iss": bad_iss, "exp": 9999999999},
        secret_main,
        algorithm="HS256",
    )
    assert verify_and_decode_jwt(token_bad_iss_main) is None
    res_b = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_bad_iss_main}"})
    assert res_b.status_code == 401


def test_correct_issuer_accepted_for_supabase_tokens(monkeypatch):
    """Verify that tokens signed with SUPABASE_JWT_SECRET with the exact matching issuer are accepted."""
    secret_main = "m" * 64
    secret_supabase = "s" * 64
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret_main)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret_supabase)
    _profile_cache.clear()

    user_id = "d082c415-67b4-5c33-bc25-62e65c25241a"
    exact_iss = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"

    token_correct_iss = jwt.encode(
        {
            "sub": user_id,
            "email": "exam.director.1@examops.institution.edu",
            "role": "ACADEMIC_ADMINISTRATOR",
            "iss": exact_iss,
            "exp": 9999999999,
        },
        secret_supabase,
        algorithm="HS256",
    )
    payload = verify_and_decode_jwt(token_correct_iss)
    assert payload is not None
    assert payload["iss"] == exact_iss
    assert payload["sub"] == user_id

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_correct_iss}"})
    assert res.status_code == 200
    assert res.json()["id"] == user_id


def test_internal_examops_tokens_without_issuer_accepted(monkeypatch):
    """Verify internal ExamOps tokens signed with JWT_SECRET_KEY without an 'iss' claim remain valid."""
    secret_main = "m" * 64
    secret_supabase = "s" * 64
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret_main)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret_supabase)
    _profile_cache.clear()

    user_id = "d082c415-67b4-5c33-bc25-62e65c25241a"
    token_internal = create_access_token(
        user_id=user_id,
        email="exam.director.1@examops.institution.edu",
        role="ACADEMIC_ADMINISTRATOR",
    )

    payload = verify_and_decode_jwt(token_internal)
    assert payload is not None
    assert payload.get("iss") is None
    assert payload["sub"] == user_id

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_internal}"})
    assert res.status_code == 200
    assert res.json()["id"] == user_id


def test_token_with_missing_or_incorrect_issuer_does_not_fall_through(monkeypatch):
    """Verify that a token with invalid/missing issuer under SUPABASE_JWT_SECRET never falls through to JWT_SECRET_KEY."""
    secret_main = "m" * 64
    secret_supabase = "s" * 64
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret_main)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret_supabase)
    _profile_cache.clear()

    user_id = "d082c415-67b4-5c33-bc25-62e65c25241a"

    # Token signed with SUPABASE_JWT_SECRET but missing 'iss'
    token_supabase_no_iss = jwt.encode(
        {"sub": user_id, "email": "test@examops.edu", "role": "LEARNER", "exp": 9999999999},
        secret_supabase,
        algorithm="HS256",
    )
    # Must be None, must not fall through to Step 3
    assert verify_and_decode_jwt(token_supabase_no_iss) is None

    # Token signed with SUPABASE_JWT_SECRET but with invalid 'iss'
    token_supabase_bad_iss = jwt.encode(
        {"sub": user_id, "email": "test@examops.edu", "role": "LEARNER", "iss": "https://attacker.com", "exp": 9999999999},
        secret_supabase,
        algorithm="HS256",
    )
    # Must be None, must not fall through to Step 3
    assert verify_and_decode_jwt(token_supabase_bad_iss) is None
