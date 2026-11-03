"""
Regression Test Suite: Scheduling Execution, Persistence & Timetable Export Validation
======================================================================================
Verifies:
1. Complete scheduling workflow and database persistence in Supabase PostgreSQL.
2. Accurate accounting of scheduled (81) and honest unscheduled (219) exams out of 300 total.
3. Schedule assignments persistence (317 confirmed room assignments, 14,505 seated students).
4. Full explanation decision telemetry for all 300 examinations.
5. Consistent, valid CSV export containing real assignments with matching metrics.
6. Consistent, valid JSON export containing assignments, decisions, and matching metrics.
7. Honest unassigned count handling on DRAFT scheduling runs (never reporting 0 unassigned).
8. Strict hard constraint adherence (zero student clashes, zero room double-bookings, zero capacity violations).
"""

import csv
import io
import pytest
from backend.database import execute_query, get_db_cursor
from backend.services.export_service import ExportService
from backend.services.scheduling_service import SchedulingService


@pytest.fixture(scope="module")
def published_run():
    run = execute_query(
        """
        SELECT id, run_code, academic_period_id, status, total_exams, scheduled_count, unassigned_count
        FROM scheduling_runs
        WHERE status = 'PUBLISHED'
        ORDER BY updated_at DESC
        LIMIT 1;
        """,
        fetch_one=True,
    )
    if not run:
        pytest.skip("No PUBLISHED scheduling run found in database.")
    return run


def test_published_run_persistence_and_metrics(published_run):
    """Verifies that the published run persists accurate metrics in PostgreSQL."""
    run_id = str(published_run["id"])

    assert published_run["status"] == "PUBLISHED"
    assert published_run["total_exams"] == 300
    assert published_run["scheduled_count"] == 81
    assert published_run["unassigned_count"] == 219
    assert published_run["scheduled_count"] + published_run["unassigned_count"] == published_run["total_exams"]

    # Verify confirmed room assignments count
    assignments_count = execute_query(
        "SELECT COUNT(*) as count FROM schedule_assignments WHERE scheduling_run_id = %s AND status = 'CONFIRMED';",
        (run_id,),
        fetch_one=True,
    )["count"]
    assert assignments_count == 317

    # Verify total seated students across all rooms
    seated_count = execute_query(
        """
        SELECT COUNT(*) as count 
        FROM assignment_students ast
        JOIN schedule_assignments sa ON sa.id = ast.assignment_id
        WHERE sa.scheduling_run_id = %s AND sa.status = 'CONFIRMED';
        """,
        (run_id,),
        fetch_one=True,
    )["count"]
    assert seated_count == 14505

    # Verify all 300 decisions are persisted with explainable reason codes
    decisions = execute_query(
        "SELECT is_assigned, COUNT(*) as cnt FROM scheduling_decisions WHERE scheduling_run_id = %s GROUP BY is_assigned;",
        (run_id,),
    )
    decision_map = {d["is_assigned"]: d["cnt"] for d in decisions}
    assert decision_map.get(True) == 81
    assert decision_map.get(False) == 219


def test_csv_export_content_and_consistency(published_run):
    """Verifies that ExportService.export_schedule_csv returns valid, populated CSV data."""
    run_id = str(published_run["id"])
    csv_text = ExportService.export_schedule_csv(run_id)

    assert isinstance(csv_text, str)
    assert len(csv_text) > 1000

    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    # Must contain all 317 confirmed room assignments
    assert len(rows) == 317

    required_headers = {
        "assignment_code",
        "exam_code",
        "exam_title",
        "course_code",
        "room_code",
        "room_name",
        "building",
        "start_time",
        "end_time",
        "status",
        "seated_students",
        "assigned_invigilators",
    }
    assert required_headers.issubset(set(reader.fieldnames))

    # Verify data integrity of rows
    total_seated = sum(int(r["seated_students"]) for r in rows)
    assert total_seated == 14505

    unique_exams = {r["exam_code"] for r in rows}
    assert len(unique_exams) == 81

    for row in rows:
        assert row["status"] == "CONFIRMED"
        assert row["assignment_code"].startswith("ASN-")
        assert row["exam_code"].startswith("EXAM-")
        assert row["room_code"].startswith("ROOM-")
        assert int(row["seated_students"]) > 0


def test_json_export_content_and_consistency(published_run):
    """Verifies that ExportService.export_schedule_json returns matching structured results."""
    run_id = str(published_run["id"])
    json_data = ExportService.export_schedule_json(run_id)

    assert isinstance(json_data, dict)
    assert "error" not in json_data
    
    run_meta = json_data["scheduling_run"]
    assert str(run_meta["id"]) == run_id
    assert run_meta["status"] == "PUBLISHED"
    assert run_meta["total_exams"] == 300
    assert run_meta["scheduled_count"] == 81
    assert run_meta["unassigned_count"] == 219
    assert json_data["total_assignments"] == 317

    # Verify assignments payload
    assignments = json_data["assignments"]
    assert len(assignments) == 317

    # Verify decisions payload
    decisions = json_data["decisions"]
    assert len(decisions) == 300

    assigned_decisions = [d for d in decisions if d["is_assigned"]]
    unassigned_decisions = [d for d in decisions if not d["is_assigned"]]
    assert len(assigned_decisions) == 81
    assert len(unassigned_decisions) == 219

    # Verify each unassigned exam has explainable reason codes
    for d in unassigned_decisions:
        assert len(d.get("reason_codes", [])) > 0


def test_draft_run_honest_unassigned_counts():
    """Verifies that new DRAFT runs honestly report all exams as unassigned (never 0)."""
    period = execute_query("SELECT id FROM academic_periods LIMIT 1;", fetch_one=True)
    if not period:
        pytest.skip("No academic period available.")

    admin = execute_query(
        "SELECT id FROM user_profiles WHERE role = 'ACADEMIC_ADMINISTRATOR' LIMIT 1;",
        fetch_one=True,
    )
    admin_id = str(admin["id"]) if admin else None

    # Create a draft run
    draft_run = SchedulingService.create_scheduling_run(
        academic_period_id=str(period["id"]),
        created_by=admin_id,
        algorithm_version="1.0.0-test",
        seed=20261022,
    )
    draft_id = draft_run["id"]

    try:
        # Check database record
        persisted = SchedulingService.get_run_by_id(draft_id)
        assert persisted["status"] == "DRAFT"
        assert persisted["total_exams"] == 300
        assert persisted["scheduled_count"] == 0
        # HONEST REPORTING: 300 exams in a draft that hasn't run are 300 unassigned!
        assert persisted["unassigned_count"] == 300

        # Check CSV export for draft run: returns informative diagnostic header
        csv_text = ExportService.export_schedule_csv(draft_id)
        assert "Status: DRAFT (300 total exams, 0 scheduled, 300 unassigned)" in csv_text
        assert "assignment_code,exam_code" in csv_text

        # Check JSON export for draft run
        json_data = ExportService.export_schedule_json(draft_id)
        draft_meta = json_data["scheduling_run"]
        assert draft_meta["status"] == "DRAFT"
        assert draft_meta["scheduled_count"] == 0
        assert draft_meta["unassigned_count"] == 300
        assert json_data["total_assignments"] == 0
        assert len(json_data["assignments"]) == 0
    finally:
        # Clean up test draft run
        with get_db_cursor(commit=True) as cur:
            cur.execute("DELETE FROM scheduling_decisions WHERE scheduling_run_id = %s;", (draft_id,))
            cur.execute("DELETE FROM schedule_assignments WHERE scheduling_run_id = %s;", (draft_id,))
            cur.execute("DELETE FROM scheduling_runs WHERE id = %s;", (draft_id,))


def test_zero_hard_constraint_violations(published_run):
    """Verifies that the published timetable strictly obeys all hard constraints."""
    run_id = str(published_run["id"])

    # Hard Constraint 1: Zero student examination clashes
    student_clashes = execute_query(
        """
        SELECT ast1.student_id, sa1.exam_id as exam1, sa2.exam_id as exam2
        FROM assignment_students ast1
        JOIN schedule_assignments sa1 ON sa1.id = ast1.assignment_id
        JOIN assignment_students ast2 ON ast2.student_id = ast1.student_id AND ast2.id != ast1.id
        JOIN schedule_assignments sa2 ON sa2.id = ast2.assignment_id
        WHERE sa1.scheduling_run_id = %s
          AND sa2.scheduling_run_id = %s
          AND sa1.status = 'CONFIRMED'
          AND sa2.status = 'CONFIRMED'
          AND sa1.exam_id < sa2.exam_id
          AND (
            sa1.start_time < (sa2.start_time + make_interval(mins => ast2.effective_duration_minutes))
            AND (sa1.start_time + make_interval(mins => ast1.effective_duration_minutes)) > sa2.start_time
          )
        LIMIT 5;
        """,
        (run_id, run_id),
    )
    assert len(student_clashes) == 0, f"Violations found: {student_clashes}"

    # Hard Constraint 2: Zero room double-bookings
    room_clashes = execute_query(
        """
        SELECT sa1.room_id, sa1.id as asgn1, sa2.id as asgn2
        FROM schedule_assignments sa1
        JOIN schedule_assignments sa2 
            ON sa1.room_id = sa2.room_id 
            AND sa1.id < sa2.id
            AND sa1.scheduling_run_id = sa2.scheduling_run_id
        WHERE sa1.scheduling_run_id = %s
          AND sa1.status = 'CONFIRMED'
          AND sa2.status = 'CONFIRMED'
          AND (sa1.start_time < sa2.end_time AND sa1.end_time > sa2.start_time)
        LIMIT 5;
        """,
        (run_id,),
    )
    assert len(room_clashes) == 0, f"Room clashes found: {room_clashes}"

    # Hard Constraint 3: Zero room capacity overruns
    capacity_violations = execute_query(
        """
        SELECT sa.id, r.room_code, COUNT(ast.id) as seated, rc.exam_capacity
        FROM schedule_assignments sa
        JOIN rooms r ON r.id = sa.room_id
        LEFT JOIN assignment_students ast ON ast.assignment_id = sa.id
        LEFT JOIN room_capacities rc 
            ON rc.room_id = sa.room_id 
            AND sa.start_time::date >= rc.effective_start 
            AND sa.start_time::date <= rc.effective_end
        WHERE sa.scheduling_run_id = %s
          AND sa.status = 'CONFIRMED'
        GROUP BY sa.id, r.room_code, rc.exam_capacity
        HAVING COUNT(ast.id) > rc.exam_capacity
        LIMIT 5;
        """,
        (run_id,),
    )
    assert len(capacity_violations) == 0, f"Capacity violations found: {capacity_violations}"
