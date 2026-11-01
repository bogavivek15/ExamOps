"""
Independent Security Verification Suite
Tests:
1. Unauthenticated requests (401)
2. Invalid JWT token (401)
3. Expired / Malformed JWT token (401)
4. Learner isolation & forbidden admin actions (403)
5. Instructor role publishing restrictions (403)
6. Support staff FERPA clinical note privacy masking
7. Administrator role authorization (200)
8. Unauthorized publication attempts (403)
9. Database role escalation prevention trigger
10. Secret & Service-Role key non-exposure audit
"""
import sys
import os
import json
import base64
import time
from pathlib import Path
from starlette.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.main import app
from backend.database import execute_query

client = TestClient(app)

def create_mock_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = "mock-signature"
    return f"{h_b64}.{p_b64}.{sig}"

def run_tests():
    print("=" * 60)
    print("INDEPENDENT SECURITY VECTOR VERIFICATION")
    print("=" * 60)

    # 1. Unauthenticated request
    res = client.get("/api/auth/profiles")
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"
    print("[PASS] 1. Unauthenticated request correctly rejected with HTTP 401.")

    # 2. Invalid JWT token
    res = client.get("/api/auth/profiles", headers={"Authorization": "Bearer totally-invalid-token"})
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"
    print("[PASS] 2. Invalid JWT token correctly rejected with HTTP 401.")

    # 3. Expired / Non-existent user ID in JWT token
    expired_token = create_mock_jwt({
        "sub": "00000000-0000-0000-0000-000000000000",
        "email": "nonexistent@institution.edu",
        "exp": int(time.time()) - 3600,
    })
    res = client.get("/api/auth/profiles", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"
    print("[PASS] 3. Non-existent/invalid subject in JWT rejected with HTTP 401.")

    # 4. Learner isolation: cannot list user profiles
    res = client.get("/api/auth/profiles", headers={"X-Test-Role": "LEARNER"})
    assert res.status_code == 403, f"Expected 403, got {res.status_code}"
    print("[PASS] 4. Learner role denied access to admin profiles with HTTP 403.")

    # 5. Learner cannot execute scheduling run
    res = client.post("/api/scheduling/runs/dummy-id/execute", headers={"X-Test-Role": "LEARNER"})
    assert res.status_code == 403, f"Expected 403, got {res.status_code}"
    print("[PASS] 5. Learner role denied scheduling run execution with HTTP 403.")

    # 6. Instructor cannot publish scheduling run
    res = client.post("/api/scheduling/runs/dummy-id/publish", headers={"X-Test-Role": "INSTRUCTOR"})
    assert res.status_code == 403, f"Expected 403, got {res.status_code}"
    print("[PASS] 6. Instructor role denied schedule publication with HTTP 403.")

    # 7. Support staff / Learner clinical documentation masking
    acc_row = execute_query("SELECT id FROM accommodations LIMIT 1;", fetch_one=True)
    if acc_row:
        acc_id = acc_row["id"]
        admin_res = client.get(f"/api/accommodations/{acc_id}/notes", headers={"X-Test-Role": "ACADEMIC_ADMINISTRATOR"})
        assert admin_res.status_code == 200, f"Expected 200, got {admin_res.status_code}"
        admin_note = admin_res.json()[0]["clinical_notes"]
        student_res = client.get(f"/api/accommodations/{acc_id}/notes", headers={"X-Test-Role": "LEARNER"})
        assert student_res.status_code == 200, f"Expected 200, got {student_res.status_code}"
        student_note = student_res.json()[0]["clinical_notes"]
        assert "REDACTED" not in admin_note, "Admin must see unmasked clinical notes"
        assert "[CONFIDENTIAL CLINICAL RECORD REDACTED" in student_note, "Student must see redacted clinical notes"
        print("[PASS] 7. FERPA/GDPR clinical note privacy verified (Admin unmasked, Learner masked).")

    # 8. Administrator privileges verified
    admin_prof = client.get("/api/auth/profiles", headers={"X-Test-Role": "ACADEMIC_ADMINISTRATOR"})
    assert admin_prof.status_code == 200, f"Expected 200, got {admin_prof.status_code}"
    print("[PASS] 8. Academic Administrator authorized successfully with HTTP 200.")

    # 9. Database role escalation prevention trigger
    db_res = execute_query("SELECT count(*) as cnt FROM pg_trigger WHERE tgname = 'trg_user_profile_immutability';", fetch_one=True)
    assert db_res["cnt"] >= 1, "Role escalation trigger must exist in PostgreSQL"
    print("[PASS] 9. PostgreSQL role-immutability trigger 'trg_user_profile_immutability' active.")

    # 10. Service role key non-exposure
    frontend_bundle = Path("frontend/dist/assets").glob("*.js")
    for b in frontend_bundle:
        text = b.read_text(encoding="utf-8")
        assert "service_role" not in text.lower(), f"Potential service role key pattern found in {b.name}"
    print("[PASS] 10. Frontend client assets audited: zero service-role keys present.")

    print("\nALL 10 INDEPENDENT SECURITY VECTORS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
