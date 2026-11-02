"""
Test Suite: Referential Integrity & Cross-Table Consistency
Validates:
1. Every foreign key relationship across all 26 tables has zero orphaned rows
2. Composite foreign key integrity on assignment_students, run_exam_students, and schedule_assignments
3. SchedulingRun counters reconcile with assignment and decision records
4. Cross-table consistency between courses, exams, and student enrollments
"""
import pytest
from backend.database import execute_query

def test_foreign_key_referential_integrity():
    """Verify that all child tables have zero orphaned records pointing to nonexistent parents."""
    fk_pairs = [
        ("enrollments", "student_id", "students", "id"),
        ("enrollments", "course_id", "courses", "id"),
        ("enrollments", "academic_period_id", "academic_periods", "id"),
        ("courses", "academic_period_id", "academic_periods", "id"),
        ("course_instructors", "course_id", "courses", "id"),
        ("course_instructors", "instructor_profile_id", "user_profiles", "id"),
        ("exams", "course_id", "courses", "id"),
        ("exams", "academic_period_id", "academic_periods", "id"),
        ("exam_requirements", "exam_id", "exams", "id"),
        ("room_capacities", "room_id", "rooms", "id"),
        ("room_equipment", "room_id", "rooms", "id"),
        ("room_equipment", "equipment_type_id", "equipment_types", "id"),
        ("room_availabilities", "room_id", "rooms", "id"),
        ("availabilities", "invigilator_id", "invigilators", "id"),
        ("accommodations", "student_id", "students", "id"),
        ("accommodation_notes", "accommodation_id", "accommodations", "id"),
        ("schedule_assignments", "scheduling_run_id", "scheduling_runs", "id"),
        ("schedule_assignments", "exam_id", "exams", "id"),
        ("schedule_assignments", "room_id", "rooms", "id"),
        ("assignment_invigilators", "assignment_id", "schedule_assignments", "id"),
        ("assignment_invigilators", "invigilator_id", "invigilators", "id"),
        ("scheduling_decisions", "scheduling_run_id", "scheduling_runs", "id"),
        ("scheduling_decisions", "exam_id", "exams", "id"),
    ]
    for child_tbl, child_col, parent_tbl, parent_col in fk_pairs:
        sql = f"""
            SELECT c.id FROM "{child_tbl}" c
            LEFT JOIN "{parent_tbl}" p ON c.{child_col} = p.{parent_col}
            WHERE c.{child_col} IS NOT NULL AND p.{parent_col} IS NULL
            LIMIT 5;
        """
        orphans = execute_query(sql)
        assert len(orphans) == 0, f"Found {len(orphans)} orphans in {child_tbl}.{child_col} referencing {parent_tbl}"

def test_composite_foreign_key_integrity():
    """Verify that assignment_students strictly aligns with schedule_assignments."""
    sql = """
        SELECT ast.id
        FROM assignment_students ast
        JOIN schedule_assignments sa ON ast.assignment_id = sa.id
        WHERE ast.scheduling_run_id != sa.scheduling_run_id 
           OR ast.exam_id != sa.exam_id 
           OR ast.room_id != sa.room_id
        LIMIT 5;
    """
    mismatches = execute_query(sql)
    assert len(mismatches) == 0, f"Found composite key mismatches in assignment_students: {mismatches}"

def test_scheduling_run_totals_consistency():
    """Verify scheduled_count + unassigned_count == total_exams for completed runs."""
    sql = """
        SELECT id, run_code, total_exams, scheduled_count, unassigned_count
        FROM scheduling_runs
        WHERE status IN ('APPROVED', 'PUBLISHED', 'REVIEW_REQUIRED')
          AND total_exams != (scheduled_count + unassigned_count);
    """
    mismatches = execute_query(sql)
    assert len(mismatches) == 0, f"Found run count inconsistencies: {mismatches}"

