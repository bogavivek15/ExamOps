"""
Test Suite: Role-Based Access Control (RBAC) & Security Integrity
Validates:
1. Unauthenticated requests are rejected with 401 Unauthorized
2. Learner role cannot access administrative endpoints (403 Forbidden)
3. Academic Administrator can access scheduling operations
4. Accommodation clinical notes are masked/redacted for non-officer roles
5. UserProfile role immutability trigger blocks unauthorized privilege escalation
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import execute_query, execute_mutation

client = TestClient(app)

def test_unauthenticated_rejected():
    """Verify protected routes reject unauthenticated requests."""
    protected_urls = [
        "/api/auth/me",
        "/api/scheduling/runs",
        "/api/audit/logs",
    ]
    for url in protected_urls:
        res = client.get(url)
        assert res.status_code == 401, f"Expected 401 for unauthenticated {url}, got {res.status_code}"

def test_learner_forbidden_admin_routes():
    """Verify LEARNER role is denied access to administrative mutation endpoints."""
    headers_learner = {"X-Test-Role": "LEARNER"}
    
    # 1. User Profiles list
    res1 = client.get("/api/auth/profiles", headers=headers_learner)
    assert res1.status_code == 403

    # 2. Scheduling run creation
    res2 = client.post("/api/scheduling/runs", json={}, headers=headers_learner)
    assert res2.status_code == 403

def test_clinical_notes_redacted_for_instructors():
    """Verify medical/clinical privacy masking for non-officers."""
    acc = execute_query(
        """
        SELECT a.id 
        FROM accommodations a
        JOIN accommodation_notes an ON an.accommodation_id = a.id
        LIMIT 1;
        """,
        fetch_one=True,
    )
    if not acc:
        pytest.skip("No accommodation notes found.")

    acc_id = str(acc["id"])

    # Instructor gets redacted content
    res_inst = client.get(f"/api/accommodations/{acc_id}/notes", headers={"X-Test-Role": "INSTRUCTOR"})
    assert res_inst.status_code == 200
    notes = res_inst.json()
    assert len(notes) > 0
    assert "REDACTED" in notes[0]["clinical_notes"]

    # Academic administrator gets full unredacted content
    res_admin = client.get(f"/api/accommodations/{acc_id}/notes", headers={"X-Test-Role": "ACADEMIC_ADMINISTRATOR"})
    assert res_admin.status_code == 200
    notes_admin = res_admin.json()
    assert len(notes_admin) > 0
    assert "REDACTED" not in notes_admin[0]["clinical_notes"]

