"""
ExamOps Automated Authentication & Role Revocation Tests
Verifies immediate & <= 5-second role revocation propagation, privilege downgrade enforcement,
account deactivation, token expiration, signature integrity, and unauthorized direct API rejection.
"""
import pytest
import time
import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import (
    create_access_token,
    verify_and_decode_jwt,
    _profile_cache,
    invalidate_profile_cache,
)
from backend.database import execute_query, execute_mutation, get_db_cursor

client = TestClient(app)

@pytest.fixture
def ephemeral_test_user():
    """Creates a temporary isolated user profile in PostgreSQL for testing role changes."""
    user_id = str(uuid.uuid4())
    email = f"audit_user_{user_id[:8]}@examops.institution.edu"
    sql = """
    INSERT INTO user_profiles (id, email, display_name, role, status, department)
    VALUES (%s, %s, %s, 'ACADEMIC_ADMINISTRATOR', 'ACTIVE', 'Computer Science')
    RETURNING *;
    """
    with get_db_cursor(commit=True) as cur:
        cur.execute(sql, (user_id, email, "Revocation Test Admin"))
        user = cur.fetchone()

    yield user

    # Cleanup user profile
    invalidate_profile_cache(f"user:{user_id}")
    execute_mutation("DELETE FROM user_profiles WHERE id = %s;", (user_id,))

def test_admin_to_learner_role_downgrade(ephemeral_test_user):
    """
    Verifies that downgrading an administrator to LEARNER takes effect
    immediately or within <= 5 seconds, resulting in HTTP 403 Forbidden.
    """
    user_id = str(ephemeral_test_user["id"])
    email = ephemeral_test_user["email"]
    token = create_access_token(user_id=user_id, email=email, role="ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. As administrator, listing profiles succeeds
    res_initial = client.get("/api/auth/profiles", headers=headers)
    assert res_initial.status_code == 200, res_initial.text

    # 2. Downgrade user role in PostgreSQL to LEARNER
    execute_mutation("UPDATE user_profiles SET role = 'LEARNER' WHERE id = %s;", (user_id,))
    # Immediate invalidation
    invalidate_profile_cache(f"user:{user_id}")

    # 3. Direct API call with original token -> Backend must check DB and reject with 403
    res_downgraded = client.get("/api/auth/profiles", headers=headers)
    assert res_downgraded.status_code == 403
    assert "Forbidden" in res_downgraded.json()["detail"]

def test_learner_promoted_to_admin(ephemeral_test_user):
    """Verifies that promoting a LEARNER to ACADEMIC_ADMINISTRATOR immediately grants access."""
    user_id = str(ephemeral_test_user["id"])
    email = ephemeral_test_user["email"]

    # Start as LEARNER
    execute_mutation("UPDATE user_profiles SET role = 'LEARNER' WHERE id = %s;", (user_id,))
    invalidate_profile_cache(f"user:{user_id}")

    token = create_access_token(user_id=user_id, email=email, role="LEARNER")
    headers = {"Authorization": f"Bearer {token}"}

    res_blocked = client.get("/api/auth/profiles", headers=headers)
    assert res_blocked.status_code == 403

    # Promote to ACADEMIC_ADMINISTRATOR
    execute_mutation("UPDATE user_profiles SET role = 'ACADEMIC_ADMINISTRATOR' WHERE id = %s;", (user_id,))
    invalidate_profile_cache(f"user:{user_id}")

    res_promoted = client.get("/api/auth/profiles", headers=headers)
    assert res_promoted.status_code == 200

def test_account_deactivation_revokes_access(ephemeral_test_user):
    """Verifies that deactivating an account immediately produces HTTP 401 Unauthorized."""
    user_id = str(ephemeral_test_user["id"])
    email = ephemeral_test_user["email"]
    token = create_access_token(user_id=user_id, email=email, role="ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {token}"}

    # Verify active access
    res_active = client.get("/api/auth/profiles", headers=headers)
    assert res_active.status_code == 200

    # Deactivate account in PostgreSQL
    execute_mutation("UPDATE user_profiles SET status = 'INACTIVE' WHERE id = %s;", (user_id,))
    invalidate_profile_cache(f"user:{user_id}")

    # Access must be refused
    res_deactivated = client.get("/api/auth/profiles", headers=headers)
    assert res_deactivated.status_code == 401

def test_cache_ttl_bounds_cross_worker_revocation(ephemeral_test_user):
    """
    Verifies that even if another worker does not receive in-process invalidation,
    the maximum privilege window is strictly bounded by the 5.0-second TTL.
    """
    user_id = str(ephemeral_test_user["id"])
    email = ephemeral_test_user["email"]
    token = create_access_token(user_id=user_id, email=email, role="ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {token}"}

    # Prime the in-memory cache
    res1 = client.get("/api/auth/profiles", headers=headers)
    assert res1.status_code == 200

    # Downgrade directly in PostgreSQL WITHOUT calling invalidate_profile_cache (simulating separate worker)
    execute_mutation("UPDATE user_profiles SET role = 'LEARNER' WHERE id = %s;", (user_id,))

    # Verify cache TTL property
    assert _profile_cache.ttl <= 5.0, f"ProfileCache TTL must be <= 5.0s, was {_profile_cache.ttl}"

    # Wait for TTL to expire (5.1 seconds)
    time.sleep(5.1)

    # After TTL, the cache must have expired and fetched the downgraded role from PostgreSQL
    res2 = client.get("/api/auth/profiles", headers=headers)
    assert res2.status_code == 403, f"Expected 403 after TTL expiry, got {res2.status_code}"

def test_expired_jwt_rejected():
    """Verifies that an expired JWT token is rejected with HTTP 401."""
    # Create token expired 60 seconds ago
    token = create_access_token(
        user_id=str(uuid.uuid4()),
        email="expired@test.com",
        role="ACADEMIC_ADMINISTRATOR",
        expires_delta_seconds=-60,
    )
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/auth/profiles", headers=headers)
    assert res.status_code == 401

def test_invalid_jwt_signature_rejected():
    """Verifies that a tampered JWT signature is rejected with HTTP 401."""
    token = create_access_token(
        user_id=str(uuid.uuid4()),
        email="tampered@test.com",
        role="ACADEMIC_ADMINISTRATOR",
    )
    parts = token.split(".")
    # Tamper with signature
    tampered = f"{parts[0]}.{parts[1]}.tampered_signature_payload"
    headers = {"Authorization": f"Bearer {tampered}"}
    res = client.get("/api/auth/profiles", headers=headers)
    assert res.status_code == 401

def test_direct_api_access_without_authorization():
    """Verifies that requests missing authentication credentials are systematically rejected."""
    # No auth header at all
    res_no_auth = client.get("/api/auth/profiles")
    assert res_no_auth.status_code == 401
    
    # Missing authorization for admin action
    res_no_role = client.post("/api/scheduling/runs", json={})
    assert res_no_role.status_code == 401

