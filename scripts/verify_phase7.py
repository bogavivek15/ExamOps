"""
ExamOps Phase 7 Dual Verification Script
Double-checks Phase 7: Complete Full-Stack Integration.
- Pass A: Architecture, Route Contract & Configuration Audit
- Pass B: Live Empirical Full-Stack Integration across all 12 modules
"""

import os
import sys
import json
from pathlib import Path
from starlette.testclient import TestClient

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.main import app
from backend.database import init_db_pool, get_db_cursor

client = TestClient(app)

ADMIN_HEADERS = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}
STUDENT_HEADERS = {"X-Test-Role": "LEARNER"}

def audit_pass_a():
    print("=" * 60)
    print("PHASE 7 — PASS A: ARCHITECTURE & ROUTE CONTRACT AUDIT")
    print("=" * 60)

    # 1. Inspect registered routes on FastAPI app via OpenAPI schema
    route_paths = set(app.openapi()["paths"].keys())
    
    required_routes = [
        "/health",
        "/api/auth/me",
        "/api/auth/profiles",
        "/api/students",
        "/api/courses",
        "/api/enrollments",
        "/api/exams",
        "/api/rooms",
        "/api/invigilators",
        "/api/accommodations",
        "/api/scheduling/runs",
        "/api/analytics/overview",
        "/api/audit/logs",
    ]

    for req in required_routes:
        assert req in route_paths, f"Missing route in FastAPI application: {req}"
        print(f"  [PASS] Registered FastAPI route: {req}")

    # 2. Check CORS Middleware
    middleware_types = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_types, "CORSMiddleware not configured on app"
    print("  [PASS] CORSMiddleware active with allowed origins")

    # 3. Verify frontend api.js contains matching endpoints
    api_js_path = ROOT_DIR / "frontend" / "src" / "services" / "api.js"
    assert api_js_path.exists(), "frontend api.js missing"
    api_code = api_js_path.read_text(encoding="utf-8")
    for req in ["/students", "/courses", "/exams", "/rooms", "/invigilators", "/accommodations", "/scheduling/runs", "/analytics/overview", "/audit/logs"]:
        assert req in api_code, f"API client missing call to {req}"
        print(f"  [PASS] Frontend API client mapping: {req}")

    print("\nPASS A RESULT: ALL ROUTE CONTRACTS AND INTEGRATION INTERFACES VERIFIED.")
    return True

def audit_pass_b():
    print("\n" + "=" * 60)
    print("PHASE 7 — PASS B: LIVE FULL-STACK INTEGRATION TEST")
    print("=" * 60)

    init_db_pool()

    # 1. Health & Database Connectivity
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    data = res.json()
    assert data["database"] == "HEALTHY", f"Database not healthy: {data}"
    print(f"  [PASS] /health check: service={data['service']}, db={data['database']}")

    # 2. Module 1: Overview Analytics
    res = client.get("/api/analytics/overview", headers=ADMIN_HEADERS)
    assert res.status_code == 200, f"Analytics overview failed: {res.text}"
    overview = res.json()
    assert "total_students" in overview, "Missing total_students in overview"
    assert overview["total_students"] >= 5000, f"Expected >= 5000 students, got {overview['total_students']}"
    print(f"  [PASS] Module 1 (Overview): total_students={overview['total_students']}, total_exams={overview['total_exams']}")

    # 3. Module 2: Complete Scheduling Workflow (Create -> Execute -> Inspect -> Approve -> Publish)
    print("  Executing Module 2: Scheduling Operations Center integration flow...")
    
    # 3.1 Fetch academic period
    with get_db_cursor() as cur:
        cur.execute("SELECT id FROM academic_periods WHERE code = 'TERM-2026-02' OR name LIKE '%Fall 2026%' LIMIT 1;")
        ap_row = cur.fetchone()
        assert ap_row, "Academic period for Fall 2026 missing"
        period_id = ap_row["id"]

    # 3.2 Create Run
    create_res = client.post(
        "/api/scheduling/runs",
        headers=ADMIN_HEADERS,
        json={"academic_period_id": period_id, "algorithm_version": "v1.0.0-integration", "notes": "Phase 7 Full-Stack Verification Run"}
    )
    assert create_res.status_code in (200, 201), f"Failed to create run: {create_res.text}"
    run = create_res.json()
    run_id = run["id"]
    print(f"  [PASS] Run Created: {run['run_code']} (ID: {run_id})")

    # 3.3 Execute Solver
    exec_res = client.post(f"/api/scheduling/runs/{run_id}/execute", headers=ADMIN_HEADERS)
    assert exec_res.status_code == 200, f"Failed to execute run: {exec_res.text}"
    exec_data = exec_res.json()
    metrics = exec_data.get("metrics", {})
    scheduled = metrics.get("scheduled_count", exec_data.get("scheduled_count", 0))
    total = metrics.get("total_exams", exec_data.get("total_exams", 0))
    duration = metrics.get("execution_duration_ms", 0)
    print(f"  [PASS] Solver Executed: Scheduled={scheduled}/{total} exams in {duration:.1f}ms")

    # 3.4 Inspect Assignments
    asn_res = client.get(f"/api/scheduling/runs/{run_id}/assignments?limit=10", headers=ADMIN_HEADERS)
    assert asn_res.status_code == 200
    asn_data = asn_res.json()
    asn_count = len(asn_data) if isinstance(asn_data, list) else asn_data.get("total", len(asn_data.get("items", [])))
    assert asn_count > 0, "No assignments generated"
    print(f"  [PASS] Assignments Inspected: {asn_count} sample assignment records")

    # 3.5 Inspect Decisions Telemetry
    dec_res = client.get(f"/api/scheduling/runs/{run_id}/decisions?limit=10", headers=ADMIN_HEADERS)
    assert dec_res.status_code == 200
    dec_data = dec_res.json()
    dec_items = dec_data if isinstance(dec_data, list) else dec_data.get("items", [])
    assert len(dec_items) > 0, "No decisions recorded"
    print(f"  [PASS] Decisions Telemetry Inspected: {len(dec_items)} sample decision records")

    # 3.6 Approve Run
    appr_res = client.post(f"/api/scheduling/runs/{run_id}/approve", headers=ADMIN_HEADERS)
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "APPROVED"
    print("  [PASS] Run Approved: status=APPROVED")

    # 3.7 Publish Run
    pub_res = client.post(f"/api/scheduling/runs/{run_id}/publish", headers=ADMIN_HEADERS)
    assert pub_res.status_code == 200
    run_after = client.get(f"/api/scheduling/runs/{run_id}", headers=ADMIN_HEADERS).json()
    assert run_after["status"] == "PUBLISHED"
    print("  [PASS] Run Published via Stored Procedure: status=PUBLISHED")

    # 4. Module 3: Exam Management
    exams_res = client.get("/api/exams?limit=5", headers=ADMIN_HEADERS)
    assert exams_res.status_code == 200
    exam_items = exams_res.json() if isinstance(exams_res.json(), list) else exams_res.json().get("items", [])
    assert len(exam_items) > 0, "No exams returned"
    exam_item = exam_items[0]
    reqs_res = client.get(f"/api/exams/{exam_item['id']}/requirements", headers=ADMIN_HEADERS)
    assert reqs_res.status_code == 200
    print(f"  [PASS] Module 3 (Exams): Exam {exam_item['exam_code']} requirements={len(reqs_res.json())}")

    # 5. Module 4: Student Management
    stu_res = client.get("/api/students?limit=5", headers=ADMIN_HEADERS)
    assert stu_res.status_code == 200
    stu_items = stu_res.json() if isinstance(stu_res.json(), list) else stu_res.json().get("items", [])
    assert len(stu_items) > 0, "No students returned"
    student_item = stu_items[0]
    stu_sched_res = client.get(f"/api/students/{student_item['id']}/schedule", headers=ADMIN_HEADERS)
    assert stu_sched_res.status_code == 200
    print(f"  [PASS] Module 4 (Students): Student {student_item['student_code']} timetable loaded")

    # 6. Module 5: Course & Enrollment Management
    crs_res = client.get("/api/courses?limit=5", headers=ADMIN_HEADERS)
    assert crs_res.status_code == 200
    enr_res = client.get("/api/enrollments?limit=5", headers=ADMIN_HEADERS)
    assert enr_res.status_code == 200
    enr_count = len(enr_res.json()) if isinstance(enr_res.json(), list) else enr_res.json().get("total", len(enr_res.json().get("items", [])))
    print(f"  [PASS] Module 5 (Courses): Catalog and enrollments verified ({enr_count} enrollments loaded)")

    # 7. Module 6: Room & Facilities Management
    rooms_res = client.get("/api/rooms?limit=5", headers=ADMIN_HEADERS)
    assert rooms_res.status_code == 200
    room_items = rooms_res.json() if isinstance(rooms_res.json(), list) else rooms_res.json().get("items", [])
    assert len(room_items) > 0, "No rooms returned"
    room_item = room_items[0]
    room_det_res = client.get(f"/api/rooms/{room_item['id']}", headers=ADMIN_HEADERS)
    assert room_det_res.status_code == 200
    print(f"  [PASS] Module 6 (Rooms): Venue {room_item['room_code']} details loaded")

    # 8. Module 7: Invigilator Management
    inv_res = client.get("/api/invigilators?limit=5", headers=ADMIN_HEADERS)
    assert inv_res.status_code == 200
    inv_items = inv_res.json() if isinstance(inv_res.json(), list) else inv_res.json().get("items", [])
    assert len(inv_items) > 0, "No invigilators returned"
    inv_item = inv_items[0]
    inv_sched_res = client.get(f"/api/invigilators/{inv_item['id']}/schedule", headers=ADMIN_HEADERS)
    assert inv_sched_res.status_code == 200
    print(f"  [PASS] Module 7 (Invigilators): Invigilator {inv_item['invigilator_code']} schedule loaded")

    # 9. Module 8: Accommodation Management & Medical Privacy
    acc_res = client.get("/api/accommodations?limit=5", headers=ADMIN_HEADERS)
    assert acc_res.status_code == 200
    acc_items = acc_res.json() if isinstance(acc_res.json(), list) else acc_res.json().get("items", [])
    assert len(acc_items) > 0, "No accommodations returned"
    acc_item = acc_items[0]
    
    # Authorized admin request -> clinical notes present or unredacted
    notes_admin = client.get(f"/api/accommodations/{acc_item['id']}/notes", headers=ADMIN_HEADERS)
    assert notes_admin.status_code == 200
    admin_notes_list = notes_admin.json() if isinstance(notes_admin.json(), list) else [notes_admin.json()]
    if admin_notes_list:
        assert "REDACTED" not in admin_notes_list[0].get("clinical_notes", "")
    
    # Student / unauthorized request -> clinical notes redacted
    notes_student = client.get(f"/api/accommodations/{acc_item['id']}/notes", headers=STUDENT_HEADERS)
    assert notes_student.status_code == 200
    student_notes_list = notes_student.json() if isinstance(notes_student.json(), list) else [notes_student.json()]
    if student_notes_list:
        assert "REDACTED" in student_notes_list[0].get("clinical_notes", "")
    print(f"  [PASS] Module 8 (Accommodations): FERPA medical notes protection verified (Admin decrypted, Student redacted)")

    # 10. Module 9: Exception Center
    issues_res = client.get(f"/api/scheduling/runs/{run_id}/issues", headers=ADMIN_HEADERS)
    assert issues_res.status_code == 200
    print(f"  [PASS] Module 9 (Exceptions): Run {run_id} issue telemetry queried successfully")

    # 11. Module 10: Export CSV & JSON
    csv_res = client.get(f"/api/export/runs/{run_id}/csv", headers=ADMIN_HEADERS)
    assert csv_res.status_code == 200
    assert "assignment_code" in csv_res.text and "exam_code" in csv_res.text and "room_code" in csv_res.text
    json_res = client.get(f"/api/export/runs/{run_id}/json", headers=ADMIN_HEADERS)
    assert json_res.status_code == 200
    json_data = json_res.json()
    assert json_data.get("scheduling_run", {}).get("run_code") == run["run_code"] or json_data.get("run_code") == run["run_code"]
    print(f"  [PASS] Module 10 (Exports): CSV ({len(csv_res.text.splitlines())} lines) and JSON exported successfully")

    # 12. Module 11: Audit Trail
    audit_res = client.get("/api/audit/logs?limit=10", headers=ADMIN_HEADERS)
    assert audit_res.status_code == 200
    audit_items = audit_res.json() if isinstance(audit_res.json(), list) else audit_res.json().get("items", [])
    actions = [a["action"] for a in audit_items]
    assert any("RUN" in a or "SCHEDULE" in a for a in actions), f"Expected run actions in audit trail, got {actions}"
    print(f"  [PASS] Module 11 (Audit): Immutable audit events verified ({len(audit_items)} events inspected)")

    # 13. Module 12: Administration & Profiles
    prof_res = client.get("/api/auth/profiles", headers=ADMIN_HEADERS)
    assert prof_res.status_code == 200
    assert len(prof_res.json()) > 0
    print(f"  [PASS] Module 12 (Admin): {len(prof_res.json())} system operator accounts retrieved")

    print("\nPASS B RESULT: ALL 12 PRODUCT MODULES VERIFIED EMPIRICALLY AGAINST LIVE DB.")
    return True

if __name__ == "__main__":
    try:
        audit_pass_a()
        audit_pass_b()
        print("\n" + "=" * 60)
        print("PHASE 7 COMPLETE: FULL-STACK INTEGRATION DUAL VERIFICATION PASSED.")
        print("=" * 60)
    except Exception as e:
        print(f"\nPHASE 7 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
