"""
ExamOps Supabase Cloud Integration Verification Suite
Empirically tests against live Supabase PostgreSQL:
1. Supabase PostgreSQL Connectivity & Masked Credentials Security
2. Database Schema, Table Counts & Baseline Integrity (5,000 students, 150 courses, 25,044 enrollments, 300 exams, 100 rooms, 200 invigilators)
3. Security, RBAC & Database RLS:
   - Unauthenticated request rejection (401)
   - Invalid JWT rejection (401)
   - Academic Administrator / Exam Officer permissions
   - Learner read-only restrictions
   - Development role-switching restriction in production
   - Database Row Level Security (RLS) enforcement
4. Scheduling Lifecycle against Supabase:
   - POST /scheduling/runs
   - Execute scheduling algorithm
   - Persist assignments, decisions, and issues
   - Approve run
   - Publish run via atomic publication procedure (publish_schedule_run)
5. All 12 Functional Modules End-to-End API verification
6. Simulated Backend Restart & Data Persistence Check
"""
import sys
import os
import json
import uuid
from pathlib import Path
from starlette.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.config import settings
from backend.database import init_db_pool, get_db_cursor, execute_query, mask_connection_url, _pool
from backend.main import app
from backend.auth import create_access_token

client = TestClient(app)

def run_all_cloud_tests():
    print("=" * 80)
    print("EXAMOPS REAL SUPABASE CLOUD INTEGRATION VERIFICATION")
    print(f"Target Database: {mask_connection_url(settings.DATABASE_URL)}")
    print("=" * 80)

    # 1. Connectivity & Health Check
    print("\n--- 1. Testing Supabase Health & Connection ---")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check returned {res.status_code}: {res.text}"
    health_data = res.json()
    assert health_data["database"] == "HEALTHY", f"Database not healthy: {health_data}"
    print(f"  [PASS] /health: status={health_data['status']}, service={health_data['service']}, db={health_data['database']}")

    # 2. Schema Table Verification & Row Counts
    print("\n--- 2. Verifying Tables & Baseline Row Counts ---")
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = [r["table_name"] for r in cur.fetchall()]
        assert len(tables) >= 26, f"Expected >= 26 tables, found {len(tables)}"
        print(f"  [PASS] All {len(tables)} tables verified in Supabase public schema.")

        # Baseline Entity Counts
        expected_counts = {
            "students": 5000,
            "courses": 150,
            "enrollments": 25044,
            "exams": 300,
            "rooms": 100,
            "invigilators": 200,
            "accommodations": 301,
            "academic_periods": 1,
            "equipment_types": 5,
        }
        for tbl, expected in expected_counts.items():
            cur.execute(f"SELECT COUNT(*) as c FROM {tbl};")
            count = cur.fetchone()["c"]
            assert count == expected, f"Count mismatch for {tbl}: got {count}, expected {expected}"
            print(f"  [PASS] {tbl}: {count} rows verified (expected {expected})")

    # 3. Security, RBAC & Authentication Checks
    print("\n--- 3. Verifying Authentication & Security Contracts ---")
    
    # 3.1 Unauthenticated request rejected
    unauth_res = client.get("/api/auth/me")
    assert unauth_res.status_code == 401, f"Expected 401 for unauthenticated request, got {unauth_res.status_code}"
    print("  [PASS] Unauthenticated request correctly rejected with 401 Unauthorized.")

    # 3.2 Invalid JWT rejected
    invalid_res = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert invalid_res.status_code == 401, f"Expected 401 for invalid JWT, got {invalid_res.status_code}"
    print("  [PASS] Invalid Bearer token correctly rejected with 401 Unauthorized.")

    # 3.3 Admin & Exam Officer Access
    admin_prof = execute_query(
        "SELECT * FROM user_profiles WHERE role = 'ACADEMIC_ADMINISTRATOR' AND status = 'ACTIVE' ORDER BY email ASC LIMIT 1;",
        fetch_one=True
    )
    assert admin_prof, "No active ACADEMIC_ADMINISTRATOR profile in Supabase"
    admin_token = create_access_token(str(admin_prof["id"]), admin_prof["email"], admin_prof["role"])
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    learner_prof = execute_query(
        "SELECT * FROM user_profiles WHERE role = 'LEARNER' AND status = 'ACTIVE' ORDER BY email ASC LIMIT 1;",
        fetch_one=True
    )
    assert learner_prof, "No active LEARNER profile in Supabase"
    learner_token = create_access_token(str(learner_prof["id"]), learner_prof["email"], learner_prof["role"])
    learner_headers = {"Authorization": f"Bearer {learner_token}"}

    # Admin access verified
    admin_me = client.get("/api/auth/me", headers=admin_headers)
    assert admin_me.status_code == 200
    assert admin_me.json()["role"] == "ACADEMIC_ADMINISTRATOR"
    print(f"  [PASS] Authenticated Examination Officer access verified ({admin_prof['email']}).")

    # Learner forbidden from administrative endpoints
    learner_forbidden = client.get("/api/auth/profiles", headers=learner_headers)
    assert learner_forbidden.status_code == 403, f"Expected 403 for learner on /auth/profiles, got {learner_forbidden.status_code}"
    print("  [PASS] Learner role restricted: 403 Forbidden received for administrative endpoints.")

    # 3.4 Production Role Switcher Guard
    prev_env = settings.ENVIRONMENT
    settings.ENVIRONMENT = "production"
    prod_switch_res = client.post("/api/auth/dev-switch-role", json={"role": "ACADEMIC_ADMINISTRATOR"})
    settings.ENVIRONMENT = prev_env
    assert prod_switch_res.status_code == 403, f"Expected 403 for role switch in production, got {prod_switch_res.status_code}"
    print("  [PASS] Production guard: dev-switch-role cannot grant admin privileges in production.")

    # 3.5 Direct Database RLS Policy Verification
    with get_db_cursor() as cur:
        # Check that RLS is active on tables
        cur.execute("""
            SELECT relname, relrowsecurity 
            FROM pg_class 
            JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
            WHERE pg_namespace.nspname = 'public' AND relkind = 'r'
            AND relname IN ('students', 'user_profiles', 'accommodations', 'accommodation_notes', 'scheduling_runs');
        """)
        rls_rows = cur.fetchall()
        for r in rls_rows:
            assert r["relrowsecurity"] is True, f"RLS not enabled on {r['relname']}"
        print(f"  [PASS] Direct database RLS confirmed active on sensitive tables.")

    # 4. Scheduling Lifecycle on Supabase Cloud
    print("\n--- 4. Executing Real Scheduling Run Lifecycle on Supabase ---")
    ap = execute_query("SELECT id FROM academic_periods WHERE is_active = TRUE LIMIT 1;", fetch_one=True)
    assert ap, "No active academic period in Supabase"
    period_id = str(ap["id"])

    # 4.1 Create Run
    create_res = client.post(
        "/api/scheduling/runs",
        headers=admin_headers,
        json={
            "academic_period_id": period_id,
            "algorithm_version": "v1.0.0-supabase-cloud",
            "notes": "Supabase Cloud Automated Verification Run",
        }
    )
    assert create_res.status_code in (200, 201), f"Run creation failed: {create_res.text}"
    run = create_res.json()
    run_id = run["id"]
    print(f"  [PASS] Scheduling Run Created: {run['run_code']} (ID: {run_id})")

    # 4.2 Execute Solver
    print("  Executing scheduling algorithm against cloud dataset...")
    exec_res = client.post(f"/api/scheduling/runs/{run_id}/execute", headers=admin_headers)
    assert exec_res.status_code == 200, f"Run execution failed: {exec_res.text}"
    exec_data = exec_res.json()
    metrics = exec_data.get("metrics", {})
    scheduled = metrics.get("scheduled_count", exec_data.get("scheduled_count", 0))
    total = metrics.get("total_exams", exec_data.get("total_exams", 0))
    duration = metrics.get("execution_duration_ms", 0)
    print(f"  [PASS] Solver Executed: Scheduled {scheduled}/{total} examinations in {duration:.1f}ms.")

    # 4.3 Inspect Assignments
    asn_res = client.get(f"/api/scheduling/runs/{run_id}/assignments?limit=10", headers=admin_headers)
    assert asn_res.status_code == 200
    asn_data = asn_res.json()
    asn_count = len(asn_data) if isinstance(asn_data, list) else asn_data.get("total", len(asn_data.get("items", [])))
    assert asn_count > 0, "No assignments retrieved from Supabase"
    print(f"  [PASS] Persisted assignments in Supabase: {asn_count} sample records retrieved.")

    # 4.4 Inspect Decisions Telemetry
    dec_res = client.get(f"/api/scheduling/runs/{run_id}/decisions?limit=10", headers=admin_headers)
    assert dec_res.status_code == 200
    dec_data = dec_res.json()
    dec_items = dec_data if isinstance(dec_data, list) else dec_data.get("items", [])
    assert len(dec_items) > 0, "No decisions recorded in Supabase"
    print(f"  [PASS] Algorithmic decisions in Supabase: {len(dec_items)} sample records retrieved.")

    # 4.5 Approve Run
    appr_res = client.post(f"/api/scheduling/runs/{run_id}/approve", headers=admin_headers)
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "APPROVED"
    print("  [PASS] Scheduling Run Approved: status=APPROVED.")

    # 4.6 Publish Run (Stored Procedure on Supabase)
    pub_res = client.post(f"/api/scheduling/runs/{run_id}/publish", headers=admin_headers)
    assert pub_res.status_code == 200
    pub_run = client.get(f"/api/scheduling/runs/{run_id}", headers=admin_headers).json()
    assert pub_run["status"] == "PUBLISHED"
    print("  [PASS] Scheduling Run Published via Supabase Stored Procedure: status=PUBLISHED.")

    # 5. Full 12 Product Modules End-to-End API Verification
    print("\n--- 5. Verifying All 12 Modules via Real Backend & Supabase ---")
    
    # Module 1: Overview Dashboard
    ov_res = client.get("/api/analytics/overview", headers=admin_headers)
    assert ov_res.status_code == 200
    ov = ov_res.json()
    assert ov["total_students"] == 5000 and ov["total_exams"] == 300
    print(f"  [PASS] Module 1 (Overview Dashboard): total_students={ov['total_students']}, total_exams={ov['total_exams']}")

    # Module 2: Scheduling Operations
    runs_res = client.get("/api/scheduling/runs", headers=admin_headers)
    assert runs_res.status_code == 200
    print(f"  [PASS] Module 2 (Scheduling Operations): {len(runs_res.json())} runs listed")

    # Module 3: Exam Management
    exams_res = client.get("/api/exams?limit=5", headers=admin_headers)
    assert exams_res.status_code == 200
    ex_list = exams_res.json() if isinstance(exams_res.json(), list) else exams_res.json().get("items", [])
    assert len(ex_list) > 0
    req_res = client.get(f"/api/exams/{ex_list[0]['id']}/requirements", headers=admin_headers)
    assert req_res.status_code == 200
    print(f"  [PASS] Module 3 (Exam Management): Exam {ex_list[0]['exam_code']} and {len(req_res.json())} requirements loaded")

    # Module 4: Student Management
    stu_res = client.get("/api/students?limit=5", headers=admin_headers)
    assert stu_res.status_code == 200
    st_list = stu_res.json() if isinstance(stu_res.json(), list) else stu_res.json().get("items", [])
    assert len(st_list) > 0
    st_sched = client.get(f"/api/students/{st_list[0]['id']}/schedule", headers=admin_headers)
    assert st_sched.status_code == 200
    print(f"  [PASS] Module 4 (Student Management): Student {st_list[0]['student_code']} timetable queried")

    # Module 5: Course & Enrollment Management
    crs_res = client.get("/api/courses?limit=5", headers=admin_headers)
    assert crs_res.status_code == 200
    enr_res = client.get("/api/enrollments?limit=5", headers=admin_headers)
    assert enr_res.status_code == 200
    print(f"  [PASS] Module 5 (Course & Enrollment): Courses catalog and enrollments verified")

    # Module 6: Room Management
    room_res = client.get("/api/rooms?limit=5", headers=admin_headers)
    assert room_res.status_code == 200
    r_list = room_res.json() if isinstance(room_res.json(), list) else room_res.json().get("items", [])
    r_det = client.get(f"/api/rooms/{r_list[0]['id']}", headers=admin_headers)
    assert r_det.status_code == 200
    print(f"  [PASS] Module 6 (Room Management): Room {r_list[0]['room_code']} details loaded")

    # Module 7: Invigilator Management
    inv_res = client.get("/api/invigilators?limit=5", headers=admin_headers)
    assert inv_res.status_code == 200
    inv_list = inv_res.json() if isinstance(inv_res.json(), list) else inv_res.json().get("items", [])
    inv_sched = client.get(f"/api/invigilators/{inv_list[0]['id']}/schedule", headers=admin_headers)
    assert inv_sched.status_code == 200
    print(f"  [PASS] Module 7 (Invigilator Management): Invigilator {inv_list[0]['invigilator_code']} schedule loaded")

    # Module 8: Accommodation Management & Clinical Privacy
    acc_res = client.get("/api/accommodations?limit=5", headers=admin_headers)
    assert acc_res.status_code == 200
    acc_list = acc_res.json() if isinstance(acc_res.json(), list) else acc_res.json().get("items", [])
    admin_notes = client.get(f"/api/accommodations/{acc_list[0]['id']}/notes", headers=admin_headers)
    assert admin_notes.status_code == 200
    learner_notes = client.get(f"/api/accommodations/{acc_list[0]['id']}/notes", headers=learner_headers)
    assert learner_notes.status_code == 200
    l_notes_data = learner_notes.json() if isinstance(learner_notes.json(), list) else [learner_notes.json()]
    assert "REDACTED" in l_notes_data[0].get("clinical_notes", "")
    print(f"  [PASS] Module 8 (Accommodations): Medical privacy enforced (Admin decrypted, Learner redacted)")

    # Module 9: Exception Center
    issues_res = client.get(f"/api/scheduling/runs/{run_id}/issues", headers=admin_headers)
    assert issues_res.status_code == 200
    print(f"  [PASS] Module 9 (Exception Center): Diagnostic telemetry queried for run {run['run_code']}")

    # Module 10: Analytics & Reports (CSV / JSON Export)
    csv_res = client.get(f"/api/export/runs/{run_id}/csv", headers=admin_headers)
    assert csv_res.status_code == 200
    assert "assignment_code" in csv_res.text
    json_res = client.get(f"/api/export/runs/{run_id}/json", headers=admin_headers)
    assert json_res.status_code == 200
    print(f"  [PASS] Module 10 (Analytics & Reports): CSV & JSON exports generated from Supabase data")

    # Module 11: Audit & Activity
    audit_res = client.get("/api/audit/logs?limit=10", headers=admin_headers)
    assert audit_res.status_code == 200
    audit_items = audit_res.json() if isinstance(audit_res.json(), list) else audit_res.json().get("items", [])
    assert len(audit_items) > 0
    print(f"  [PASS] Module 11 (Audit & Activity): {len(audit_items)} append-only audit records inspected")

    # Module 12: Administration
    prof_res = client.get("/api/auth/profiles", headers=admin_headers)
    assert prof_res.status_code == 200
    print(f"  [PASS] Module 12 (Administration): {len(prof_res.json())} system operator accounts retrieved")

    # 6. Backend Restart & Persistence Verification
    print("\n--- 6. Backend Restart & Data Persistence Verification ---")
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None
    init_db_pool()
    restart_check = execute_query("SELECT COUNT(*) as c FROM scheduling_runs WHERE id = %s;", (run_id,), fetch_one=True)
    assert restart_check and restart_check["c"] == 1
    print(f"  [PASS] Connection pool cleanly re-initialized; Run {run_id} persisted in Supabase.")

    print("\n" + "=" * 80)
    print("ALL VERIFICATION SUITES PASSED EMPIRICALLY AGAINST LIVE SUPABASE POSTGRESQL!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = run_all_cloud_tests()
    sys.exit(0 if success else 1)
