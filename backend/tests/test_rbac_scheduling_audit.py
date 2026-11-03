"""
Test Suite: Definitive Role-Based Access Control, Student Privacy & Scheduling Integrity Audit
Verifies:
1. Platform Administrator vs Academic Administrator distinct permission boundaries
2. Course Instructor and Support Staff restricted views and blocked mutation controls
3. Student / Learner strict data isolation and privacy protection across all endpoints
4. Scheduling Run published immutability: Re-execution is rejected with HTTP 400
5. Full 5-role validation matching docs/permissions.md specifications
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import execute_query
from backend.auth import create_access_token

client = TestClient(app)

@pytest.fixture(scope="module")
def published_run():
    run = execute_query(
        "SELECT id, run_code, status FROM scheduling_runs WHERE status = 'PUBLISHED' ORDER BY updated_at DESC LIMIT 1;",
        fetch_one=True,
    )
    if not run:
        pytest.skip("No PUBLISHED scheduling run found in database.")
    return run

@pytest.fixture(scope="module")
def demo_students():
    # Carlos Garcia (STU-000008) and another student
    s1 = execute_query(
        "SELECT id, student_code, email FROM students WHERE student_code = 'STU-000008' LIMIT 1;",
        fetch_one=True,
    )
    s2 = execute_query(
        "SELECT id, student_code, email FROM students WHERE student_code = 'STU-000009' LIMIT 1;",
        fetch_one=True,
    )
    return s1, s2

# ==============================================================================
# 1. PLATFORM ADMINISTRATOR TESTS
# ==============================================================================

def test_platform_administrator_permissions(published_run):
    """Platform Administrator has full governance access including user profile mutation."""
    headers = {"X-Test-Role": "PLATFORM_ADMINISTRATOR"}

    # 1. Can view user profiles
    res_prof = client.get("/api/auth/profiles?limit=5", headers=headers)
    assert res_prof.status_code == 200

    # 2. Can inspect decisions
    run_id = str(published_run["id"])
    res_dec = client.get(f"/api/scheduling/runs/{run_id}/decisions?limit=5", headers=headers)
    assert res_dec.status_code == 200

    # 3. Can inspect audit logs
    res_audit = client.get("/api/audit/logs?limit=5", headers=headers)
    assert res_audit.status_code == 200

    # 4. Can export schedules
    res_exp = client.get(f"/api/export/runs/{run_id}/csv", headers=headers)
    assert res_exp.status_code == 200

# ==============================================================================
# 2. ACADEMIC ADMINISTRATOR TESTS & DISTINCT PERMISSION BOUNDARIES
# ==============================================================================

def test_academic_administrator_distinct_permissions(published_run):
    """
    Academic Administrator can operate scheduling and read profiles,
    but is FORBIDDEN from mutating user profiles (distinct from Platform Administrator).
    """
    headers = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}
    run_id = str(published_run["id"])

    # 1. Can view user profiles (Read only)
    res_prof = client.get("/api/auth/profiles?limit=5", headers=headers)
    assert res_prof.status_code == 200

    # 2. CANNOT mutate user profiles (PATCH /profiles/{id} is strictly Platform Administrator only)
    dummy_uuid = str(uuid.uuid4())
    res_patch = client.patch(
        f"/api/auth/profiles/{dummy_uuid}",
        json={"display_name": "Unauthorized Attempt"},
        headers=headers,
    )
    assert res_patch.status_code == 403
    assert "Forbidden" in res_patch.json().get("detail", "")

    # 3. Can inspect decisions
    res_dec = client.get(f"/api/scheduling/runs/{run_id}/decisions?limit=5", headers=headers)
    assert res_dec.status_code == 200

    # 4. Can inspect validation issues
    res_issues = client.get(f"/api/scheduling/runs/{run_id}/issues", headers=headers)
    assert res_issues.status_code == 200

# ==============================================================================
# 3. COURSE INSTRUCTOR RESTRICTIONS
# ==============================================================================

def test_course_instructor_restrictions(published_run):
    """
    Course Instructor can view curriculum and published examinations,
    but has zero access to scheduling mutation, algorithm decisions, or facility duties.
    """
    headers = {"X-Test-Role": "INSTRUCTOR"}
    run_id = str(published_run["id"])

    # 1. Can view courses and exams
    assert client.get("/api/courses?limit=5", headers=headers).status_code == 200
    assert client.get("/api/exams?limit=5", headers=headers).status_code == 200

    # 2. CANNOT create scheduling runs
    res_create = client.post("/api/scheduling/runs", json={"academic_period_id": "none"}, headers=headers)
    assert res_create.status_code == 403

    # 3. CANNOT execute scheduling solver
    res_exec = client.post(f"/api/scheduling/runs/{run_id}/execute", headers=headers)
    assert res_exec.status_code == 403

    # 4. CANNOT approve or publish
    assert client.post(f"/api/scheduling/runs/{run_id}/approve", headers=headers).status_code == 403
    assert client.post(f"/api/scheduling/runs/{run_id}/publish", headers=headers).status_code == 403

    # 5. CANNOT inspect algorithm decisions
    assert client.get(f"/api/scheduling/runs/{run_id}/decisions", headers=headers).status_code == 403

    # 6. CANNOT inspect validation issues
    assert client.get(f"/api/scheduling/runs/{run_id}/issues", headers=headers).status_code == 403

    # 7. CANNOT export schedules
    assert client.get(f"/api/export/runs/{run_id}/csv", headers=headers).status_code == 403

    # 8. CANNOT view invigilator shifts/schedules
    dummy_inv = str(uuid.uuid4())
    assert client.get(f"/api/invigilators/{dummy_inv}/schedule", headers=headers).status_code == 403
    assert client.get(f"/api/invigilators/{dummy_inv}/availabilities", headers=headers).status_code == 403

# ==============================================================================
# 4. SUPPORT STAFF / INVIGILATOR RESTRICTIONS
# ==============================================================================

def test_support_staff_restrictions(published_run):
    """
    Support Staff can triage facilities and validation issues,
    but cannot create/execute scheduling runs, inspect algorithm telemetry, or view audit logs.
    """
    headers = {"X-Test-Role": "SUPPORT_STAFF"}
    run_id = str(published_run["id"])

    # 1. Can view rooms and validation issues for facilities triage
    assert client.get("/api/rooms?limit=5", headers=headers).status_code == 200
    assert client.get(f"/api/scheduling/runs/{run_id}/issues", headers=headers).status_code == 200

    # 2. CANNOT create or execute scheduling runs
    assert client.post("/api/scheduling/runs", json={}, headers=headers).status_code == 403
    assert client.post(f"/api/scheduling/runs/{run_id}/execute", headers=headers).status_code == 403
    assert client.post(f"/api/scheduling/runs/{run_id}/approve", headers=headers).status_code == 403
    assert client.post(f"/api/scheduling/runs/{run_id}/publish", headers=headers).status_code == 403

    # 3. CANNOT inspect algorithm decisions
    assert client.get(f"/api/scheduling/runs/{run_id}/decisions", headers=headers).status_code == 403

    # 4. CANNOT view audit logs
    assert client.get("/api/audit/logs", headers=headers).status_code == 403

    # 5. CANNOT view user profiles
    assert client.get("/api/auth/profiles", headers=headers).status_code == 403

# ==============================================================================
# 5. STUDENT / LEARNER PRIVACY & STRICT ISOLATION
# ==============================================================================

def test_student_data_isolation(demo_students, published_run):
    """
    Learner role must only access their own schedule and profile.
    Cross-student inspections and institutional assignment tables must be strictly rejected.
    """
    s1, s2 = demo_students
    s1_id = str(s1["id"])
    s2_id = str(s2["id"])

    # Resolve active learner profile for Carlos Garcia
    prof = execute_query(
        "SELECT id, email, role, student_id FROM user_profiles WHERE student_id = %s LIMIT 1;",
        (s1_id,),
        fetch_one=True,
    )
    assert prof is not None

    token_s1 = create_access_token(user_id=str(prof["id"]), email=prof["email"], role="LEARNER")
    headers_s1 = {"Authorization": f"Bearer {token_s1}"}

    # 1. GET /api/students returns ONLY own record
    res_list = client.get("/api/students", headers=headers_s1)
    assert res_list.status_code == 200
    stu_items = res_list.json()
    assert len(stu_items) == 1
    assert stu_items[0]["id"] == s1_id

    # 2. GET /api/students/{own_id} succeeds
    assert client.get(f"/api/students/{s1_id}", headers=headers_s1).status_code == 200

    # 3. Cross-student access: GET /api/students/{other_id} is rejected with 403
    res_other = client.get(f"/api/students/{s2_id}", headers=headers_s1)
    assert res_other.status_code == 403
    assert "Forbidden" in res_other.json().get("detail", "")

    # 4. Cross-student schedule: GET /api/students/{other_id}/schedule is rejected with 403
    res_other_sched = client.get(f"/api/students/{s2_id}/schedule", headers=headers_s1)
    assert res_other_sched.status_code == 403
    assert "Forbidden" in res_other_sched.json().get("detail", "")

    # 5. Own schedule: GET /api/students/{own_id}/schedule succeeds and shows published assignments
    res_own_sched = client.get(f"/api/students/{s1_id}/schedule", headers=headers_s1)
    assert res_own_sched.status_code == 200
    sched = res_own_sched.json()
    assert len(sched) > 0
    for entry in sched:
        assert "room_code" in entry
        assert "start_time" in entry
        assert "exam_code" in entry

    # 6. Institutional assignment tables are strictly FORBIDDEN for learners
    run_id = str(published_run["id"])
    res_asgns = client.get(f"/api/scheduling/runs/{run_id}/assignments", headers=headers_s1)
    assert res_asgns.status_code == 403
    assert "Forbidden" in res_asgns.json().get("detail", "")

    # 7. Other staff-only endpoints are rejected with 403 for learners
    assert client.get("/api/invigilators", headers=headers_s1).status_code == 403
    assert client.get("/api/analytics/overview", headers=headers_s1).status_code == 403
    assert client.get("/api/audit/logs", headers=headers_s1).status_code == 403
    assert client.get(f"/api/scheduling/runs/{run_id}/decisions", headers=headers_s1).status_code == 403
    assert client.get(f"/api/scheduling/runs/{run_id}/issues", headers=headers_s1).status_code == 403
    assert client.get(f"/api/export/runs/{run_id}/csv", headers=headers_s1).status_code == 403

# ==============================================================================
# 6. SCHEDULING INTEGRITY & PUBLISHED-RUN IMMUTABILITY
# ==============================================================================

def test_published_run_immutability(published_run):
    """
    Hard Constraint: A PUBLISHED scheduling run must NEVER be re-executed or overwritten.
    Attempting execution on a PUBLISHED run must return HTTP 400 with explicit rejection message.
    """
    run_id = str(published_run["id"])
    headers = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}

    res = client.post(f"/api/scheduling/runs/{run_id}/execute", headers=headers)
    assert res.status_code == 400
    err_detail = res.json().get("detail", "")
    assert "already PUBLISHED and cannot be re-executed" in err_detail

    # Verify run remains in PUBLISHED status and was NOT altered to CANCELLED or DRAFT
    current_run = client.get(f"/api/scheduling/runs/{run_id}", headers=headers).json()
    assert current_run["status"] == "PUBLISHED"
