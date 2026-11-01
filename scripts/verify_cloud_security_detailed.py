import os
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import get_db_cursor, execute_query
from backend.main import app
from backend.auth import create_access_token
from starlette.testclient import TestClient

client = TestClient(app)

def test_database_connection_role():
    print("\n--- 1. Testing Database Connection Role & RLS Bypass ---")
    with get_db_cursor() as cur:
        cur.execute("SELECT current_user, session_user, usesuper, usebypassrls FROM pg_user WHERE usename = current_user;")
        row = cur.fetchone()
        print(f"Current User: {row['current_user']}")
        print(f"Is Superuser: {row['usesuper']}")
        print(f"Bypasses RLS by Default: {row['usebypassrls']}")
        
        # Check table RLS status
        cur.execute("""
            SELECT relname, relrowsecurity, relforcerowsecurity 
            FROM pg_class 
            JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
            WHERE pg_namespace.nspname = 'public' 
            AND relname IN ('students', 'accommodations', 'accommodation_notes', 'audit_logs', 'scheduling_runs');
        """)
        for r in cur.fetchall():
            print(f"Table: {r['relname']:<22} RLS Enabled: {r['relrowsecurity']} | Force RLS: {r['relforcerowsecurity']}")

def test_immutable_triggers():
    print("\n--- 2. Testing Database-Level Immutability Triggers ---")
    log = execute_query("SELECT id FROM audit_logs LIMIT 1;", fetch_one=True)
    if not log:
        print("No audit log to test immutability on!")
        return
    log_id = log['id']
    
    # Try to UPDATE audit_logs directly via SQL
    update_blocked = False
    try:
        with get_db_cursor(commit=True) as cur:
            cur.execute("UPDATE audit_logs SET action = 'TAMPERED' WHERE id = %s;", (log_id,))
    except Exception as e:
        update_blocked = True
        print(f"  [PASS] Database rejected UPDATE on audit_logs: {e.pgcode} - {str(e).strip().splitlines()[0]}")
    assert update_blocked, "FAIL: Database allowed UPDATE on immutable audit_logs!"

    # Try to DELETE audit_logs directly via SQL
    delete_blocked = False
    try:
        with get_db_cursor(commit=True) as cur:
            cur.execute("DELETE FROM audit_logs WHERE id = %s;", (log_id,))
    except Exception as e:
        delete_blocked = True
        print(f"  [PASS] Database rejected DELETE on audit_logs: {e.pgcode} - {str(e).strip().splitlines()[0]}")
    assert delete_blocked, "FAIL: Database allowed DELETE on immutable audit_logs!"

def test_api_rbac_and_privacy():
    print("\n--- 3. Testing Administrator vs Learner Access & FERPA Privacy ---")
    
    admin_prof = execute_query(
        "SELECT * FROM user_profiles WHERE role = 'ACADEMIC_ADMINISTRATOR' AND status = 'ACTIVE' LIMIT 1;",
        fetch_one=True
    )
    admin_token = create_access_token(str(admin_prof["id"]), admin_prof["email"], admin_prof["role"])
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    learner_prof = execute_query(
        "SELECT * FROM user_profiles WHERE role = 'LEARNER' AND status = 'ACTIVE' LIMIT 1;",
        fetch_one=True
    )
    learner_token = create_access_token(str(learner_prof["id"]), learner_prof["email"], learner_prof["role"])
    learner_headers = {"Authorization": f"Bearer {learner_token}"}

    # 1. Admin can access admin endpoints
    r = client.get("/api/auth/profiles", headers=admin_headers)
    print(f"Admin /api/auth/profiles: HTTP {r.status_code} (Count: {len(r.json())})")
    assert r.status_code == 200

    # 2. Learner is forbidden from admin endpoints
    r = client.get("/api/auth/profiles", headers=learner_headers)
    print(f"Learner /api/auth/profiles: HTTP {r.status_code} ({r.json().get('detail')})")
    assert r.status_code == 403

    # 3. Learner cannot trigger scheduling
    ap = execute_query("SELECT id FROM academic_periods WHERE is_active = TRUE LIMIT 1;", fetch_one=True)
    r = client.post("/api/scheduling/runs", headers=learner_headers, json={"academic_period_id": str(ap["id"])})
    print(f"Learner POST /api/scheduling/runs: HTTP {r.status_code} ({r.json().get('detail')})")
    assert r.status_code == 403

    # 4. Sensitive Accommodation Clinical Notes
    acc = execute_query("SELECT id FROM accommodations LIMIT 1;", fetch_one=True)
    acc_id = str(acc["id"])

    # Admin gets full clinical notes
    r_admin = client.get(f"/api/accommodations/{acc_id}/notes", headers=admin_headers)
    admin_notes = r_admin.json()
    print(f"Admin GET accommodation notes: HTTP {r_admin.status_code}, Clinical text present: {bool(admin_notes[0].get('clinical_notes'))}")
    assert r_admin.status_code == 200
    assert "REDACTED" not in admin_notes[0].get("clinical_notes", "")

    # Learner gets REDACTED notes
    r_learner = client.get(f"/api/accommodations/{acc_id}/notes", headers=learner_headers)
    learner_notes = r_learner.json()
    print(f"Learner GET accommodation notes: HTTP {r_learner.status_code}, Clinical text: '{learner_notes[0].get('clinical_notes')}'")
    assert r_learner.status_code == 200
    assert "REDACTED" in learner_notes[0].get("clinical_notes", "")

if __name__ == '__main__':
    test_database_connection_role()
    test_immutable_triggers()
    test_api_rbac_and_privacy()

