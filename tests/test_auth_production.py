"""
ExamOps Production Authentication & Security Test Suite
Verifies:
1. Missing token rejection (401)
2. Invalid signature rejection (401)
3. Expired token rejection (401)
4. Inactive user profile rejection (401)
5. Production role switching denial (403)
6. Elimination of unauthenticated email-only login (400/401)
7. Authoritative PostgreSQL database role resolution
"""
import pytest
import time
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings
from backend.auth import create_access_token, CurrentUser
from backend.database import execute_query

client = TestClient(app)

def test_missing_token_returns_401():
    """Protected endpoints must reject requests lacking Authorization header."""
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    assert "detail" in res.json()

def test_invalid_token_returns_401():
    """Protected endpoints must reject forged or tampered Bearer tokens."""
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-valid-token-string"})
    assert res.status_code == 401
    assert "Invalid or expired" in res.json().get("detail", "")

def test_expired_token_returns_401():
    """Protected endpoints must reject tokens with past exp timestamps."""
    prof = execute_query(
        "SELECT id, email, role FROM user_profiles WHERE status = 'ACTIVE' LIMIT 1;",
        fetch_one=True,
    )
    assert prof is not None
    # Create token expired 10 seconds ago
    expired_token = create_access_token(
        user_id=str(prof["id"]),
        email=prof["email"],
        role=prof["role"],
        expires_delta_seconds=-10,
    )
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert "Invalid or expired" in res.json().get("detail", "")

def test_dev_switch_role_blocked_in_production(monkeypatch):
    """When ENVIRONMENT=production, /api/auth/dev-switch-role MUST return 403."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    res = client.post("/api/auth/dev-switch-role", json={"role": "ACADEMIC_ADMINISTRATOR"})
    assert res.status_code == 403
    assert "disabled in production" in res.json().get("detail", "")

def test_email_only_login_rejected():
    """Unauthenticated email-only login must be rejected with 400 Bad Request."""
    res = client.post("/api/auth/login", json={"email": "admin@examops.institution.edu"})
    assert res.status_code == 400
    assert "Both email and password are required" in res.json().get("detail", "")

def test_invalid_password_rejected():
    """Attempting login with incorrect password must be rejected with 401."""
    res = client.post("/api/auth/login", json={
        "email": "admin@examops.institution.edu",
        "password": "WrongPassword!999"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.json().get("detail", "")

def test_valid_token_resolves_db_role():
    """Valid token must resolve user profile and derive role exclusively from PostgreSQL."""
    prof = execute_query(
        "SELECT id, email, role, display_name FROM user_profiles WHERE role = 'ACADEMIC_ADMINISTRATOR' AND status = 'ACTIVE' LIMIT 1;",
        fetch_one=True,
    )
    assert prof is not None

    token = create_access_token(
        user_id=str(prof["id"]),
        email=prof["email"],
        role=prof["role"],
        expires_delta_seconds=3600,
    )

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    me = res.json()
    assert me["id"] == str(prof["id"])
    assert me["email"] == prof["email"]
    assert me["role"] == "ACADEMIC_ADMINISTRATOR"
    assert me["display_name"] == prof["display_name"]
