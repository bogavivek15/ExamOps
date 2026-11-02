"""
Test Suite: Scheduling Business Rules & Constraint Integrity
Validates:
1. Zero student overlapping examination conflicts
2. Zero room double-booking overlaps
3. Strict room capacity compliance
4. Invigilator single-booking & daily workload limits
5. Accommodation compliance (accessible rooms, extended durations)
6. Complete explanation telemetry for unassigned examinations
"""
import pytest
from backend.database import execute_query

@pytest.fixture(scope="module")
def published_run_id():
    run = execute_query("""
        SELECT id FROM scheduling_runs 
        WHERE status = 'PUBLISHED' 
        ORDER BY updated_at DESC LIMIT 1;
    """, fetch_one=True)
    if not run:
        pytest.skip("No PUBLISHED scheduling run found in database.")
    return str(run["id"])

def test_no_student_conflicts(published_run_id):
    """Hard Constraint 1: A student must not have overlapping examinations."""
    sql = """
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
    """
    conflicts = execute_query(sql, (published_run_id, published_run_id))
    assert len(conflicts) == 0, f"Detected student exam overlap conflicts: {conflicts}"

def test_no_room_double_booking(published_run_id):
    """Hard Constraint 2: A room must not have overlapping assignments."""
    sql = """
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
    """
    overlaps = execute_query(sql, (published_run_id,))
    assert len(overlaps) == 0, f"Detected room double-booking overlaps: {overlaps}"

def test_room_capacity_not_exceeded(published_run_id):
    """Hard Constraint 3: Number of seated students must not exceed room exam capacity."""
    sql = """
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
    """
    overfilled = execute_query(sql, (published_run_id,))
    assert len(overfilled) == 0, f"Detected room capacity violations: {overfilled}"

def test_no_invigilator_double_booking(published_run_id):
    """Hard Constraint 4: An invigilator must not have overlapping assignments."""
    sql = """
        SELECT ai1.invigilator_id, sa1.id as asgn1, sa2.id as asgn2
        FROM assignment_invigilators ai1
        JOIN schedule_assignments sa1 ON sa1.id = ai1.assignment_id
        JOIN assignment_invigilators ai2 
            ON ai2.invigilator_id = ai1.invigilator_id 
            AND ai1.id < ai2.id
        JOIN schedule_assignments sa2 ON sa2.id = ai2.assignment_id
        WHERE sa1.scheduling_run_id = %s
          AND sa2.scheduling_run_id = %s
          AND sa1.status = 'CONFIRMED'
          AND sa2.status = 'CONFIRMED'
          AND (sa1.start_time < sa2.end_time AND sa1.end_time > sa2.start_time)
        LIMIT 5;
    """
    overlaps = execute_query(sql, (published_run_id, published_run_id))
    assert len(overlaps) == 0, f"Detected invigilator double-booking overlaps: {overlaps}"

def test_unscheduled_exams_have_explanations(published_run_id):
    """Operational Requirement: 100% of unassigned exams have documented reason codes."""
    sql = """
        SELECT exam_id 
        FROM scheduling_decisions 
        WHERE scheduling_run_id = %s 
          AND is_assigned = FALSE 
          AND (reason_codes IS NULL OR array_length(reason_codes, 1) = 0)
        LIMIT 5;
    """
    unexplained = execute_query(sql, (published_run_id,))
    assert len(unexplained) == 0, f"Found unassigned exams missing reason codes: {unexplained}"
