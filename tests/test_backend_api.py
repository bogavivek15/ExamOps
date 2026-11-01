"""
ExamOps Backend Comprehensive Integration Test Suite
Validates all FastAPI routes, RBAC permissions, scheduling workflows, clinical privacy, and telemetry.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import execute_query

client = TestClient(app)

def test_health_check():
    """Verify backend health check reports database connectivity."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["service"] == "ExamOps Backend"
    assert data["database"] == "HEALTHY"

def test_authentication_required():
    """Verify unauthenticated requests to protected endpoints return 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_rbac_admin_profiles():
    """Verify user profiles list requires administrator privileges."""
    # Test with student role -> 403 Forbidden
    headers_student = {"X-Test-Role": "STUDENT"}
    res_student = client.get("/api/auth/profiles", headers=headers_student)
    assert res_student.status_code == 403

    # Test with administrator role -> 200 OK
    headers_admin = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}
    res_admin = client.get("/api/auth/profiles", headers=headers_admin)
    assert res_admin.status_code == 200
    profiles = res_admin.json()
    assert isinstance(profiles, list)
    assert len(profiles) > 0

def test_master_data_endpoints():
    """Verify listing and retrieval of students, courses, exams, rooms, and invigilators."""
    headers = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}

    # 1. Students
    res_stu = client.get("/api/students?limit=5", headers=headers)
    assert res_stu.status_code == 200
    students = res_stu.json()
    assert len(students) == 5
    first_stu_id = students[0]["id"]

    res_stu_detail = client.get(f"/api/students/{first_stu_id}", headers=headers)
    assert res_stu_detail.status_code == 200
    assert res_stu_detail.json()["id"] == first_stu_id

    # 2. Courses
    res_crs = client.get("/api/courses?limit=5", headers=headers)
    assert res_crs.status_code == 200
    assert len(res_crs.json()) > 0

    # 3. Exams
    res_exm = client.get("/api/exams?limit=5", headers=headers)
    assert res_exm.status_code == 200
    exams = res_exm.json()
    assert len(exams) == 5
    assert "enrolled_student_count" in exams[0]

    # 4. Rooms
    res_rms = client.get("/api/rooms?limit=5", headers=headers)
    assert res_rms.status_code == 200
    rooms = res_rms.json()
    assert len(rooms) == 5
    assert "standard_capacity" in rooms[0]
    assert "exam_capacity" in rooms[0]

    # 5. Invigilators
    res_inv = client.get("/api/invigilators?limit=5", headers=headers)
    assert res_inv.status_code == 200
    invs = res_inv.json()
    assert len(invs) == 5

def test_clinical_privacy_masking():
    """Verify medical clinical notes are redacted for non-officer roles."""
    # Find an accommodation with notes
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
        pytest.skip("No accommodation notes found in test database.")

    acc_id = str(acc["id"])

    # 1. As Instructor -> Notes must be redacted
    res_inst = client.get(f"/api/accommodations/{acc_id}/notes", headers={"X-Test-Role": "INSTRUCTOR"})
    assert res_inst.status_code == 200
    notes_inst = res_inst.json()
    assert len(notes_inst) > 0
    assert "REDACTED" in notes_inst[0]["clinical_notes"]

    # 2. As Academic Administrator -> Full note visible
    res_admin = client.get(f"/api/accommodations/{acc_id}/notes", headers={"X-Test-Role": "ACADEMIC_ADMINISTRATOR"})
    assert res_admin.status_code == 200
    notes_admin = res_admin.json()
    assert len(notes_admin) > 0
    assert "REDACTED" not in notes_admin[0]["clinical_notes"]

def test_scheduling_run_workflow():
    """
    Executes the complete end-to-end scheduling lifecycle:
    Create Run -> Execute Solver -> Verify Assignments & Telemetry -> Approve -> Publish
    """
    headers_admin = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}

    # Get active academic period
    period = execute_query("SELECT id FROM academic_periods WHERE is_active = TRUE LIMIT 1;", fetch_one=True)
    assert period is not None
    period_id = str(period["id"])

    # 1. Create Run
    create_payload = {
        "academic_period_id": period_id,
        "algorithm_version": "1.0.0",
        "seed": 20261022,
    }
    res_create = client.post("/api/scheduling/runs", json=create_payload, headers=headers_admin)
    assert res_create.status_code == 200
    run_data = res_create.json()
    run_id = run_data["id"]
    assert run_data["status"] == "DRAFT"

    # 2. Execute Solver
    res_exec = client.post(f"/api/scheduling/runs/{run_id}/execute", headers=headers_admin)
    assert res_exec.status_code == 200
    exec_data = res_exec.json()
    assert exec_data["success"] is True
    assert exec_data["status"] in ("COMPLETED", "REVIEW_REQUIRED")
    assert exec_data["metrics"]["scheduled_count"] > 0

    # 3. Inspect Assignments
    res_asgn = client.get(f"/api/scheduling/runs/{run_id}/assignments?limit=10", headers=headers_admin)
    assert res_asgn.status_code == 200
    assignments = res_asgn.json()
    assert len(assignments) > 0
    assert "assignment_code" in assignments[0]
    assert "room_code" in assignments[0]

    # 4. Inspect Decision Telemetry
    res_dec = client.get(f"/api/scheduling/runs/{run_id}/decisions?limit=10", headers=headers_admin)
    assert res_dec.status_code == 200
    decisions = res_dec.json()
    assert len(decisions) > 0
    assert "is_assigned" in decisions[0]

    # 5. Approve Run
    res_appr = client.post(f"/api/scheduling/runs/{run_id}/approve", headers=headers_admin)
    assert res_appr.status_code == 200
    assert res_appr.json()["status"] == "APPROVED"

    # 6. Publish Run (Atomic procedure with row lock)
    res_pub = client.post(f"/api/scheduling/runs/{run_id}/publish", headers=headers_admin)
    assert res_pub.status_code == 200
    pub_result = res_pub.json()
    assert pub_result.get("success") is True
    assert pub_result.get("published_run_id") == run_id

    # Verify Run status is now PUBLISHED in database
    run_db = client.get(f"/api/scheduling/runs/{run_id}", headers=headers_admin).json()
    assert run_db["status"] == "PUBLISHED"

def test_analytics_and_reconciliation():
    """Verify overview metrics and mathematical reconciliation."""
    headers = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}

    # 1. Overview
    res_ov = client.get("/api/analytics/overview", headers=headers)
    assert res_ov.status_code == 200
    overview = res_ov.json()
    assert overview["total_students"] == 5000
    assert overview["total_exams"] == 300
    assert overview["total_rooms"] == 100
    assert overview["total_invigilators"] == 200
    assert overview["completion_rate_pct"] > 0.0

    # 2. Reconciliation for published run
    published_run = overview.get("latest_run")
    if published_run:
        run_id = published_run["id"]
        res_rec = client.get(f"/api/analytics/runs/{run_id}/reconciliation", headers=headers)
        assert res_rec.status_code == 200
        rec = res_rec.json()
        assert rec["reconciles_exactly"] is True
        assert rec["rooms_utilized_count"] > 0
        assert rec["invigilators_utilized_count"] > 0

def test_export_formats():
    """Verify CSV and JSON schedule export downloads."""
    headers = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}
    run = execute_query("SELECT id FROM scheduling_runs WHERE status = 'PUBLISHED' LIMIT 1;", fetch_one=True)
    if not run:
        pytest.skip("No published run available for export test.")

    run_id = str(run["id"])

    # 1. CSV Export
    res_csv = client.get(f"/api/export/runs/{run_id}/csv", headers=headers)
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "assignment_code,exam_code" in res_csv.text

    # 2. JSON Export
    res_json = client.get(f"/api/export/runs/{run_id}/json", headers=headers)
    assert res_json.status_code == 200
    data = res_json.json()
    assert "scheduling_run" in data
    assert "assignments" in data
    assert len(data["assignments"]) > 0

def test_audit_logs():
    """Verify audit log captures events and restricts access to administrators."""
    # Student cannot view logs -> 403
    res_stu = client.get("/api/audit/logs", headers={"X-Test-Role": "STUDENT"})
    assert res_stu.status_code == 403

    # Admin can view logs -> 200
    res_admin = client.get("/api/audit/logs", headers={"X-Test-Role": "ACADEMIC_ADMINISTRATOR"})
    assert res_admin.status_code == 200
    logs = res_admin.json()
    assert isinstance(logs, list)
    assert len(logs) > 0
