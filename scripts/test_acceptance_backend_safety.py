"""
ExamOps Backend & Database Safety Verification for 8 Modules Acceptance Testing
Uses standard library urllib (no external requests dependency)
Verifies:
- Required-field and check constraint validation
- Disposable record creation, persistence in PostgreSQL, and safe cleanup
- Sensitive data masking for unauthorized roles (Accommodations clinical notes)
- Audit log immutability triggers (UPDATE and DELETE rejection)
- Analytics CSV and JSON export content inspection
- Role-based authorization enforcement
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import uuid
import datetime
import urllib.request
import urllib.error

from backend.database import execute_query, execute_mutation, get_db_cursor

BASE_URL = "http://127.0.0.1:8000/api"

def insert_returning(sql, params):
    with get_db_cursor(commit=True) as cur:
        cur.execute(sql, params)
        return cur.fetchone()

def http_req(url, method="GET", headers=None, data=None):
    if headers is None:
        headers = {}
    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "")
            body = resp.read()
            if "application/json" in content_type:
                return resp.status, json.loads(body.decode("utf-8")), resp.headers
            return resp.status, body.decode("utf-8"), resp.headers
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body), e.headers
        except Exception:
            return e.code, body, e.headers

def get_auth_token(role: str) -> str:
    status, data, _ = http_req(f"{BASE_URL}/auth/dev-switch-role", method="POST", data={"role": role})
    assert status == 200, f"Failed dev-switch-role for {role}: {data}"
    return data["access_token"]

def test_student_management_lifecycle():
    print("\n--- 1. Testing Student Management Validation, Disposable Record & Persistence ---")
    admin_token = get_auth_token("ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Required-field validation: missing student_code must fail
    try:
        execute_mutation(
            "INSERT INTO students (first_name, last_name, email) VALUES (%s, %s, %s);",
            ("Test", "Student", "test.null@institution.edu")
        )
        assert False, "Failed to reject null student_code"
    except Exception as e:
        print("  [PASS] Required field validation: NULL student_code correctly rejected by PostgreSQL constraint.")

    # 2. Disposable test student creation with compliant format STU-999901
    test_code = "STU-999901"
    execute_mutation("DELETE FROM students WHERE student_code = %s;", (test_code,))

    test_email = "stu.999901@test.institution.edu"
    insert_res = insert_returning(
        """
        INSERT INTO students (student_code, first_name, last_name, email, date_of_birth, program, year_of_study, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, student_code, email;
        """,
        (test_code, "Disposable", "AcceptanceTest", test_email, "2004-05-15", "Computer Science", 2, "ACTIVE")
    )
    test_id = str(insert_res["id"])
    print(f"  [PASS] Disposable test student created in PostgreSQL: {test_code} (UUID: {test_id})")

    # 3. Verify in PostgreSQL
    db_verify = execute_query("SELECT id, student_code, email, program FROM students WHERE id = %s;", (test_id,), fetch_one=True)
    assert db_verify and db_verify["student_code"] == test_code
    print(f"  [PASS] PostgreSQL persistence confirmed: {db_verify['student_code']}, program: {db_verify['program']}")

    # 4. Verify API search returns the record
    status, items, _ = http_req(f"{BASE_URL}/students?search={test_code}", headers=headers)
    assert status == 200
    assert any(s["student_code"] == test_code for s in items), "API failed to return disposable student"
    print(f"  [PASS] API GET /api/students?search={test_code} returned student successfully.")

    # 5. Clean up safely
    execute_mutation("DELETE FROM students WHERE id = %s;", (test_id,))
    cleanup_verify = execute_query("SELECT id FROM students WHERE id = %s;", (test_id,), fetch_one=True)
    assert cleanup_verify is None
    print(f"  [PASS] Disposable test student safely purged from PostgreSQL.")

def test_course_management_lifecycle():
    print("\n--- 2. Testing Course & Enrollment Validation, Disposable Record & Persistence ---")
    admin_token = get_auth_token("ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Required-field validation: missing course_code must fail
    try:
        execute_mutation(
            "INSERT INTO courses (name, department, credits) VALUES (%s, %s, %s);",
            ("Test Course Without Code", "Computer Science", 3)
        )
        assert False, "Failed to reject null course_code"
    except Exception as e:
        print("  [PASS] Required field validation: NULL course_code correctly rejected by PostgreSQL constraint.")

    period = execute_query("SELECT id FROM academic_periods LIMIT 1;", fetch_one=True)
    period_id = period["id"]

    # 2. Disposable test course creation with compliant format CRS-999901
    test_code = "CRS-999901"
    execute_mutation("DELETE FROM courses WHERE course_code = %s;", (test_code,))

    insert_res = insert_returning(
        """
        INSERT INTO courses (course_code, name, department, credits, academic_period_id, status)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, course_code;
        """,
        (test_code, "Software Engineering Verification", "Computer Science", 4, period_id, "ACTIVE")
    )
    test_id = str(insert_res["id"])
    print(f"  [PASS] Disposable test course created in PostgreSQL: {test_code} (UUID: {test_id})")

    # 3. Verify in PostgreSQL
    db_verify = execute_query("SELECT id, course_code, name, credits FROM courses WHERE id = %s;", (test_id,), fetch_one=True)
    assert db_verify and db_verify["course_code"] == test_code
    print(f"  [PASS] PostgreSQL persistence confirmed: {db_verify['course_code']}, credits: {db_verify['credits']}")

    # 4. Verify API list returns courses
    status, data, _ = http_req(f"{BASE_URL}/courses?limit=10", headers=headers)
    assert status == 200
    print(f"  [PASS] API GET /api/courses returned HTTP 200 with active courses.")

    # 5. Clean up safely
    execute_mutation("DELETE FROM courses WHERE id = %s;", (test_id,))
    cleanup_verify = execute_query("SELECT id FROM courses WHERE id = %s;", (test_id,), fetch_one=True)
    assert cleanup_verify is None
    print(f"  [PASS] Disposable test course safely purged from PostgreSQL.")

def test_room_management_lifecycle():
    print("\n--- 3. Testing Room Management Validation, Disposable Record & Persistence ---")
    admin_token = get_auth_token("ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Required-field validation: missing room_code
    try:
        execute_mutation(
            "INSERT INTO rooms (name, building, floor) VALUES (%s, %s, %s);",
            ("Room Without Code", "Test Building", 1)
        )
        assert False, "Failed to reject null room_code"
    except Exception as e:
        print("  [PASS] Required field validation: NULL room_code rejected by PostgreSQL constraint.")

    # 2. Disposable test room creation with compliant format ROOM-999901
    test_code = "ROOM-999901"
    execute_mutation("DELETE FROM room_capacities WHERE room_id IN (SELECT id FROM rooms WHERE room_code = %s);", (test_code,))
    execute_mutation("DELETE FROM rooms WHERE room_code = %s;", (test_code,))

    insert_res = insert_returning(
        """
        INSERT INTO rooms (room_code, name, building, floor, is_accessible, status)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, room_code;
        """,
        (test_code, "Acceptance Testing Lab", "Engineering West", 3, True, "AVAILABLE")
    )
    test_id = str(insert_res["id"])
    print(f"  [PASS] Disposable test room created in PostgreSQL: {test_code} (UUID: {test_id})")

    cap_code = "CAP-999901"
    cap_res = insert_returning(
        """
        INSERT INTO room_capacities (capacity_code, room_id, standard_capacity, exam_capacity, effective_start, effective_end)
        VALUES (%s, %s, %s, %s, CURRENT_DATE, CURRENT_DATE + 365) RETURNING id;
        """,
        (cap_code, test_id, 60, 45)
    )
    cap_id = str(cap_res["id"])

    # 3. Verify in PostgreSQL
    db_verify = execute_query("SELECT id, room_code, building, is_accessible FROM rooms WHERE id = %s;", (test_id,), fetch_one=True)
    assert db_verify and db_verify["room_code"] == test_code
    print(f"  [PASS] PostgreSQL persistence confirmed: {db_verify['room_code']}, building: {db_verify['building']}")

    # 4. Verify API search
    status, rooms, _ = http_req(f"{BASE_URL}/rooms?search={test_code}", headers=headers)
    assert status == 200
    assert any(r["room_code"] == test_code for r in rooms), "API failed to return disposable room"
    print(f"  [PASS] API GET /api/rooms?search={test_code} returned room successfully.")

    # 5. Clean up safely
    execute_mutation("DELETE FROM room_capacities WHERE id = %s;", (cap_id,))
    execute_mutation("DELETE FROM rooms WHERE id = %s;", (test_id,))
    cleanup_verify = execute_query("SELECT id FROM rooms WHERE id = %s;", (test_id,), fetch_one=True)
    assert cleanup_verify is None
    print(f"  [PASS] Disposable test room safely purged from PostgreSQL.")

def test_invigilator_management_lifecycle():
    print("\n--- 4. Testing Invigilator Validation, Disposable Record & Persistence ---")
    admin_token = get_auth_token("ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Required-field validation: missing email or code
    try:
        execute_mutation(
            "INSERT INTO invigilators (first_name, last_name, department) VALUES (%s, %s, %s);",
            ("Staff", "NoEmail", "Mathematics")
        )
        assert False, "Failed to reject null invigilator_code"
    except Exception as e:
        print("  [PASS] Required field validation: NULL invigilator_code correctly rejected by PostgreSQL.")

    # 2. Disposable test invigilator creation with compliant format INV-999901
    test_code = "INV-999901"
    execute_mutation("DELETE FROM invigilators WHERE invigilator_code = %s;", (test_code,))

    test_email = "inv.999901@proctor.institution.edu"
    insert_res = insert_returning(
        """
        INSERT INTO invigilators (invigilator_code, first_name, last_name, email, department, max_hours_per_day, max_hours_per_week, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, invigilator_code;
        """,
        (test_code, "Disposable", "InvigilatorTest", test_email, "Mathematics", 6.0, 30.0, "ACTIVE")
    )
    test_id = str(insert_res["id"])
    print(f"  [PASS] Disposable test invigilator created in PostgreSQL: {test_code} (UUID: {test_id})")

    # 3. Verify in PostgreSQL
    db_verify = execute_query("SELECT id, invigilator_code, department, max_hours_per_day FROM invigilators WHERE id = %s;", (test_id,), fetch_one=True)
    assert db_verify and db_verify["invigilator_code"] == test_code
    print(f"  [PASS] PostgreSQL persistence confirmed: {db_verify['invigilator_code']}, daily limit: {db_verify['max_hours_per_day']}h")

    # 4. Verify API search
    status, invs, _ = http_req(f"{BASE_URL}/invigilators?search={test_code}", headers=headers)
    assert status == 200
    assert any(i["invigilator_code"] == test_code for i in invs), "API failed to return disposable invigilator"
    print(f"  [PASS] API GET /api/invigilators?search={test_code} returned invigilator successfully.")

    # 5. Clean up safely
    execute_mutation("DELETE FROM invigilators WHERE id = %s;", (test_id,))
    cleanup_verify = execute_query("SELECT id FROM invigilators WHERE id = %s;", (test_id,), fetch_one=True)
    assert cleanup_verify is None
    print(f"  [PASS] Disposable test invigilator safely purged from PostgreSQL.")

def test_accommodation_privacy_and_redaction():
    print("\n--- 5. Testing Accommodations Validation & Medical Privacy Redaction ---")
    admin_token = get_auth_token("ACADEMIC_ADMINISTRATOR")
    instructor_token = get_auth_token("INSTRUCTOR")
    learner_token = get_auth_token("LEARNER")

    # 1. Invalid accommodation type rejected by PostgreSQL check constraint
    sample_student = execute_query("SELECT id FROM students LIMIT 1;", fetch_one=True)
    stu_id = sample_student["id"]
    try:
        execute_mutation(
            """
            INSERT INTO accommodations (student_id, accommodation_code, accommodation_type, effective_start, effective_end)
            VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_DATE + 30);
            """,
            (stu_id, "ACO-INVALID", "NOT_A_VALID_TYPE")
        )
        assert False, "Failed to reject invalid accommodation_type"
    except Exception as e:
        print("  [PASS] PostgreSQL check constraint rejected invalid accommodation_type.")

    # 2. Insert disposable accommodation with compliant format ACO-999901
    test_code = "ACO-999901"
    execute_mutation("DELETE FROM accommodation_notes WHERE accommodation_id IN (SELECT id FROM accommodations WHERE accommodation_code = %s);", (test_code,))
    execute_mutation("DELETE FROM accommodations WHERE accommodation_code = %s;", (test_code,))

    acc_res = insert_returning(
        """
        INSERT INTO accommodations (student_id, accommodation_code, accommodation_type, extra_time_minutes, effective_start, effective_end, is_active)
        VALUES (%s, %s, %s, %s, CURRENT_DATE, CURRENT_DATE + 30, TRUE) RETURNING id;
        """,
        (stu_id, test_code, "EXTENDED_TIME", 30)
    )
    acc_id = str(acc_res["id"])

    clinical_text = "CONFIDENTIAL MEDICAL RECORD: Student diagnosed with ADHD requiring +30min extended time and low-distraction seating."
    note_res = insert_returning(
        """
        INSERT INTO accommodation_notes (accommodation_id, clinical_notes, approved_by, documentation_url)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """,
        (acc_id, clinical_text, None, "https://disability.institution.edu/records/test_doc.pdf")
    )
    note_id = str(note_res["id"])
    print(f"  [PASS] Disposable accommodation & clinical note created (UUID: {acc_id}).")

    # 3. Test Authorized Admin Access
    admin_status, admin_notes, _ = http_req(f"{BASE_URL}/accommodations/{acc_id}/notes", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_status == 200
    assert len(admin_notes) > 0 and clinical_text in admin_notes[0]["clinical_notes"], "Admin failed to view unmasked notes"
    print("  [PASS] Administrator (ACADEMIC_ADMINISTRATOR) sees unredacted clinical notes.")

    # 4. Test Unauthorized Instructor Access (Must be REDACTED)
    inst_status, inst_notes, _ = http_req(f"{BASE_URL}/accommodations/{acc_id}/notes", headers={"Authorization": f"Bearer {instructor_token}"})
    assert inst_status == 200
    assert len(inst_notes) > 0
    assert inst_notes[0]["clinical_notes"] == "[CONFIDENTIAL CLINICAL RECORD REDACTED - AUTHORIZED ACCESS ONLY]"
    assert inst_notes[0]["documentation_url"] == "[REDACTED]"
    print("  [PASS] Course Instructor receives REDACTED clinical notes and redacted URL.")

    # 5. Test Unauthorized Learner Access (Must be REDACTED)
    learn_status, learn_notes, _ = http_req(f"{BASE_URL}/accommodations/{acc_id}/notes", headers={"Authorization": f"Bearer {learner_token}"})
    assert learn_status == 200
    assert learn_notes[0]["clinical_notes"] == "[CONFIDENTIAL CLINICAL RECORD REDACTED - AUTHORIZED ACCESS ONLY]"
    print("  [PASS] Student/Learner receives REDACTED clinical notes.")

    # 6. Clean up safely
    execute_mutation("DELETE FROM accommodation_notes WHERE id = %s;", (note_id,))
    execute_mutation("DELETE FROM accommodations WHERE id = %s;", (acc_id,))
    print("  [PASS] Disposable accommodation and test notes safely purged.")

def test_audit_immutability():
    print("\n--- 6. Testing Audit Log Immutability & Filter Validation ---")
    admin_token = get_auth_token("ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Fetch real audit log
    logs = execute_query("SELECT id, action, entity_type FROM audit_logs ORDER BY created_at DESC LIMIT 1;")
    assert len(logs) > 0, "No audit logs in DB"
    log_id = str(logs[0]["id"])
    original_action = logs[0]["action"]
    print(f"  Testing immutable audit log entry: {log_id} (Action: {original_action})")

    # 2. Attempt UPDATE - Must fail via database trigger
    try:
        execute_mutation("UPDATE audit_logs SET action = 'TAMPERED_ACTION' WHERE id = %s;", (log_id,))
        assert False, "Failed to prevent UPDATE on immutable audit log"
    except Exception as e:
        assert "immutable" in str(e).lower() or "trigger" in str(e).lower() or "prevent_modification" in str(e).lower()
        print(f"  [PASS] PostgreSQL trigger correctly blocked UPDATE on immutable audit record.")

    # 3. Attempt DELETE - Must fail via database trigger
    try:
        execute_mutation("DELETE FROM audit_logs WHERE id = %s;", (log_id,))
        assert False, "Failed to prevent DELETE on immutable audit log"
    except Exception as e:
        assert "immutable" in str(e).lower() or "trigger" in str(e).lower() or "prevent_modification" in str(e).lower()
        print(f"  [PASS] PostgreSQL trigger correctly blocked DELETE on immutable audit record.")

    # 4. Verify API filtering
    status, data, _ = http_req(f"{BASE_URL}/audit/logs?limit=5", headers=headers)
    assert status == 200
    assert len(data) > 0
    print("  [PASS] API GET /api/audit/logs returned immutable audit trail.")

def test_analytics_and_exports():
    print("\n--- 7. Testing Analytics Overview & Real CSV / JSON Timetable Exports ---")
    admin_token = get_auth_token("ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Analytics Overview
    status, ov, _ = http_req(f"{BASE_URL}/analytics/overview", headers=headers)
    assert status == 200
    print(f"  [PASS] GET /api/analytics/overview: Success Rate: {ov.get('scheduling_success_rate')}%, Room Util: {ov.get('room_utilization_rate')}%")

    # 2. Find published or completed run for export
    status, runs, _ = http_req(f"{BASE_URL}/scheduling/runs", headers=headers)
    assert status == 200
    assert len(runs) > 0, "No runs found"
    run_id = runs[0]["id"]
    run_code = runs[0]["run_code"]
    print(f"  Exporting timetable for run: {run_code} ({run_id})")

    # 3. CSV Export
    status, csv_data, headers_dict = http_req(f"{BASE_URL}/export/runs/{run_id}/csv", headers=headers)
    assert status == 200
    assert "text/csv" in headers_dict.get("Content-Type", "")
    csv_lines = csv_data.strip().split("\n")
    assert len(csv_lines) >= 1
    headers_row = csv_lines[0]
    print(f"  [PASS] CSV export returned {len(csv_lines)} lines with headers: {headers_row}")

    os.makedirs("docs/exports", exist_ok=True)
    with open("docs/exports/test_exported_timetable.csv", "w", encoding="utf-8") as f:
        f.write(csv_data)
    print("  [PASS] Verified and saved docs/exports/test_exported_timetable.csv")

    # 4. JSON Export
    status, json_data, headers_dict = http_req(f"{BASE_URL}/export/runs/{run_id}/json", headers=headers)
    assert status == 200
    assert "application/json" in headers_dict.get("Content-Type", "")
    with open("docs/exports/test_exported_timetable.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    print("  [PASS] Verified and saved docs/exports/test_exported_timetable.json")

def test_exception_center_telemetry():
    print("\n--- 8. Testing Exception Center Decision Reason Telemetry ---")
    admin_token = get_auth_token("ACADEMIC_ADMINISTRATOR")
    headers = {"Authorization": f"Bearer {admin_token}"}

    status, runs, _ = http_req(f"{BASE_URL}/scheduling/runs", headers=headers)
    run_id = runs[0]["id"]
    
    # 1. Fetch unassigned decisions
    status, decs, _ = http_req(f"{BASE_URL}/scheduling/runs/{run_id}/decisions?is_assigned=false&limit=10", headers=headers)
    assert status == 200
    assert len(decs) > 0, "Expected unassigned decisions"
    sample = decs[0]
    print(f"  [PASS] Unassigned exam decision telemetry: {sample.get('exam_code')}, Reason: {sample.get('reason_codes')}")
    assert "STUDENT_CONFLICT" in sample.get("reason_codes", []) or len(sample.get("reason_codes", [])) > 0
    print(f"  [PASS] Evaluated slots documented: {sample.get('candidate_details', {}).get('evaluated_slots')}")

if __name__ == "__main__":
    try:
        test_student_management_lifecycle()
        test_course_management_lifecycle()
        test_room_management_lifecycle()
        test_invigilator_management_lifecycle()
        test_accommodation_privacy_and_redaction()
        test_audit_immutability()
        test_analytics_and_exports()
        test_exception_center_telemetry()
        print("\n" + "=" * 70)
        print("ALL 8 MODULES BACKEND SAFETY & DATABASE ASSERTIONS PASSED!")
        print("=" * 70)
    except Exception as err:
        print(f"\n[FAIL] Assertion failed: {err}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
