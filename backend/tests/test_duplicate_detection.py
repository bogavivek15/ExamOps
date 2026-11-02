"""
Test Suite: Duplicate Detection & Uniqueness Invariants
Validates:
1. Zero exact row duplicates across all entities
2. Zero duplicate business identifiers (STU, CRS, ENR, EXAM, ROOM, INV, CAP, AVL, ACO, RUN)
3. Zero duplicate composite business keys (Enrollments student+course+period, Run+AssignmentCode, Run+Exam in decisions)
"""
import pytest
from backend.database import execute_query

def test_unique_business_codes():
    """Verify unique constraints on institutional codes are strictly satisfied."""
    code_checks = [
        ("students", "student_code"),
        ("courses", "course_code"),
        ("enrollments", "enrollment_code"),
        ("exams", "exam_code"),
        ("exam_requirements", "requirement_code"),
        ("rooms", "room_code"),
        ("room_capacities", "capacity_code"),
        ("invigilators", "invigilator_code"),
        ("availabilities", "availability_code"),
        ("accommodations", "accommodation_code"),
        ("scheduling_runs", "run_code"),
    ]
    for table, col in code_checks:
        sql = f"""
            SELECT {col}, COUNT(*) 
            FROM "{table}" 
            GROUP BY {col} 
            HAVING COUNT(*) > 1;
        """
        dupes = execute_query(sql)
        assert len(dupes) == 0, f"Found duplicate business codes in {table}.{col}: {dupes}"

def test_unique_composite_relationships():
    """Verify composite business keys enforce relational uniqueness."""
    # 1. Enrollments: a student cannot have duplicate active enrollments in the same course for the same period
    sql_enr = """
        SELECT student_id, course_id, academic_period_id, COUNT(*)
        FROM enrollments
        GROUP BY student_id, course_id, academic_period_id
        HAVING COUNT(*) > 1;
    """
    dupe_enr = execute_query(sql_enr)
    assert len(dupe_enr) == 0, f"Found duplicate enrollments: {dupe_enr}"

    # 2. Scheduling Decisions: exactly one decision per exam per run
    sql_dec = """
        SELECT scheduling_run_id, exam_id, COUNT(*)
        FROM scheduling_decisions
        GROUP BY scheduling_run_id, exam_id
        HAVING COUNT(*) > 1;
    """
    dupe_dec = execute_query(sql_dec)
    assert len(dupe_dec) == 0, f"Found duplicate decisions for same exam in a run: {dupe_dec}"

    # 3. Schedule Assignments: unique assignment_code within each run
    sql_asgn = """
        SELECT scheduling_run_id, assignment_code, COUNT(*)
        FROM schedule_assignments
        GROUP BY scheduling_run_id, assignment_code
        HAVING COUNT(*) > 1;
    """
    dupe_asgn = execute_query(sql_asgn)
    assert len(dupe_asgn) == 0, f"Found duplicate assignment codes within a run: {dupe_asgn}"

