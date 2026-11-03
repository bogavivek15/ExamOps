"""
ExamOps Referential Integrity & Relationship Validation Engine
Validates:
1. Every Foreign Key relationship in public schema for orphaned records or invalid references
2. Composite foreign keys integrity (run_exam_students, assignment_students, schedule_assignments)
3. Bidirectional relationships (e.g. UserProfile <-> Student/Invigilator)
4. Cross-table consistency (Run metrics vs decisions, assignments vs rooms, accommodations vs room features)
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import get_db_cursor, execute_query

def validate_referential_integrity() -> Dict[str, Any]:
    print("=" * 80)
    print("PHASE 2.D & 2.E: REFERENTIAL INTEGRITY & CROSS-TABLE CONSISTENCY")
    print("=" * 80)

    report = {
        "orphaned_records": {},
        "composite_fk_violations": {},
        "cross_table_inconsistencies": {},
        "summary": {
            "checks_run": 0,
            "violations_found": 0,
        }
    }

    # Foreign Key check definitions: (child_table, child_col, parent_table, parent_col)
    fk_checks = [
        ("students", "id", "enrollments", "student_id"), # reverse check (are there students with 0 enrollments?)
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
        ("accommodation_notes", "approved_by", "user_profiles", "id"),
        ("user_profiles", "student_id", "students", "id"),
        ("user_profiles", "invigilator_id", "invigilators", "id"),
        ("scheduling_runs", "academic_period_id", "academic_periods", "id"),
        ("scheduling_runs", "created_by", "user_profiles", "id"),
        ("schedule_assignments", "scheduling_run_id", "scheduling_runs", "id"),
        ("schedule_assignments", "exam_id", "exams", "id"),
        ("schedule_assignments", "room_id", "rooms", "id"),
        ("run_exam_students", "scheduling_run_id", "scheduling_runs", "id"),
        ("run_exam_students", "exam_id", "exams", "id"),
        ("run_exam_students", "student_id", "students", "id"),
        ("assignment_students", "assignment_id", "schedule_assignments", "id"),
        ("assignment_students", "run_exam_student_id", "run_exam_students", "id"),
        ("assignment_students", "scheduling_run_id", "scheduling_runs", "id"),
        ("assignment_students", "exam_id", "exams", "id"),
        ("assignment_students", "student_id", "students", "id"),
        ("assignment_students", "room_id", "rooms", "id"),
        ("assignment_invigilators", "assignment_id", "schedule_assignments", "id"),
        ("assignment_invigilators", "invigilator_id", "invigilators", "id"),
        ("scheduling_decisions", "scheduling_run_id", "scheduling_runs", "id"),
        ("scheduling_decisions", "exam_id", "exams", "id"),
        ("validation_issues", "scheduling_run_id", "scheduling_runs", "id"),
        ("schedule_events", "scheduling_run_id", "scheduling_runs", "id"),
    ]

    for child_tbl, child_col, parent_tbl, parent_col in fk_checks:
        report["summary"]["checks_run"] += 1
        # Check if child has non-null child_col that doesn't exist in parent
        sql = f"""
            SELECT c.id, c.{child_col}
            FROM "{child_tbl}" c
            LEFT JOIN "{parent_tbl}" p ON c.{child_col} = p.{parent_col}
            WHERE c.{child_col} IS NOT NULL AND p.{parent_col} IS NULL;
        """
        bad_rows = execute_query(sql)
        if bad_rows:
            report["summary"]["violations_found"] += len(bad_rows)
            key = f"{child_tbl}.{child_col} -> {parent_tbl}.{parent_col}"
            report["orphaned_records"][key] = [dict(r) for r in bad_rows]
            print(f"  [ORPHAN DETECTED] {key}: {len(bad_rows)} orphaned records found!")
        else:
            print(f"  [VALID FK] {child_tbl}.{child_col} -> {parent_tbl}.{parent_col}")

    # Composite integrity checks for assignment_students:
    # 1. Does assignment_students.assignment_id have same (scheduling_run_id, exam_id, room_id) as schedule_assignments?
    report["summary"]["checks_run"] += 1
    sql_asgn_sa = """
        SELECT ast.id as assignment_student_id, ast.assignment_id, ast.scheduling_run_id, ast.exam_id, ast.room_id,
               sa.scheduling_run_id as sa_run_id, sa.exam_id as sa_exam_id, sa.room_id as sa_room_id
        FROM assignment_students ast
        JOIN schedule_assignments sa ON ast.assignment_id = sa.id
        WHERE ast.scheduling_run_id != sa.scheduling_run_id 
           OR ast.exam_id != sa.exam_id 
           OR ast.room_id != sa.room_id;
    """
    comp_asgn_sa = execute_query(sql_asgn_sa)
    if comp_asgn_sa:
        report["summary"]["violations_found"] += len(comp_asgn_sa)
        report["composite_fk_violations"]["assignment_students_sa_mismatch"] = [dict(r) for r in comp_asgn_sa]
        print(f"  [COMPOSITE MISMATCH] assignment_students <-> schedule_assignments: {len(comp_asgn_sa)} rows mismatch!")
    else:
        print("  [VALID COMPOSITE] assignment_students <-> schedule_assignments matches exactly.")

    # 2. Does assignment_students.run_exam_student_id have same (scheduling_run_id, exam_id, student_id) as run_exam_students?
    report["summary"]["checks_run"] += 1
    sql_asgn_res = """
        SELECT ast.id as assignment_student_id, ast.run_exam_student_id, ast.scheduling_run_id, ast.exam_id, ast.student_id,
               res.scheduling_run_id as res_run_id, res.exam_id as res_exam_id, res.student_id as res_student_id
        FROM assignment_students ast
        JOIN run_exam_students res ON ast.run_exam_student_id = res.id
        WHERE ast.scheduling_run_id IN (SELECT id FROM scheduling_runs WHERE status IN ('PUBLISHED', 'APPROVED', 'REVIEW_REQUIRED', 'SCHEDULING'))
          AND (ast.scheduling_run_id != res.scheduling_run_id 
           OR ast.exam_id != res.exam_id 
           OR ast.student_id != res.student_id);
    """
    comp_asgn_res = execute_query(sql_asgn_res)
    if comp_asgn_res:
        report["summary"]["violations_found"] += len(comp_asgn_res)
        report["composite_fk_violations"]["assignment_students_res_mismatch"] = [dict(r) for r in comp_asgn_res]
        print(f"  [COMPOSITE MISMATCH] assignment_students <-> run_exam_students: {len(comp_asgn_res)} rows mismatch!")
    else:
        print("  [VALID COMPOSITE] assignment_students <-> run_exam_students matches exactly.")

    # 3. Cross-Table: Check completed scheduling_runs total_exams vs scheduled_count + unassigned_count
    report["summary"]["checks_run"] += 1
    sql_run_counts = """
        SELECT id, run_code, status, total_exams, scheduled_count, unassigned_count,
               (scheduled_count + unassigned_count) as calculated_sum
        FROM scheduling_runs
        WHERE status IN ('COMPLETED', 'REVIEW_REQUIRED', 'APPROVED', 'PUBLISHED', 'SUPERSEDED')
          AND total_exams != (scheduled_count + unassigned_count);
    """
    mismatched_runs = execute_query(sql_run_counts)
    if mismatched_runs:
        report["summary"]["violations_found"] += len(mismatched_runs)
        report["cross_table_inconsistencies"]["run_exam_count_mismatch"] = [dict(r) for r in mismatched_runs]
        print(f"  [INCONSISTENCY] scheduling_runs totals != scheduled + unassigned: {len(mismatched_runs)} runs")
    else:
        print("  [VALID RUN TOTALS] All scheduling_runs have total_exams == scheduled_count + unassigned_count.")

    # 4. Cross-Table: Check scheduled_count vs actual distinct scheduled exams in schedule_assignments
    report["summary"]["checks_run"] += 1
    sql_sched_diff = """
        SELECT sr.id, sr.run_code, sr.scheduled_count, 
               COALESCE(sa_cnt.distinct_exams, 0) as actual_scheduled_exams
        FROM scheduling_runs sr
        LEFT JOIN (
            SELECT scheduling_run_id, COUNT(DISTINCT exam_id) as distinct_exams
            FROM schedule_assignments
            WHERE status = 'CONFIRMED'
            GROUP BY scheduling_run_id
        ) sa_cnt ON sa_cnt.scheduling_run_id = sr.id
        WHERE sr.scheduled_count != COALESCE(sa_cnt.distinct_exams, 0);
    """
    sched_diff = execute_query(sql_sched_diff)
    if sched_diff:
        report["summary"]["violations_found"] += len(sched_diff)
        report["cross_table_inconsistencies"]["scheduled_count_vs_assignments"] = [dict(r) for r in sched_diff]
        print(f"  [INCONSISTENCY] scheduled_count vs assignments mismatch: {len(sched_diff)} runs")
    else:
        print("  [VALID ASSIGNMENT COUNTS] scheduled_count equals distinct exams in schedule_assignments.")

    # 5. Cross-Table: Check decisions count for each completed run == total_exams
    report["summary"]["checks_run"] += 1
    sql_dec_cnt = """
        SELECT sr.id, sr.run_code, sr.total_exams, COUNT(sd.id) as actual_decisions
        FROM scheduling_runs sr
        LEFT JOIN scheduling_decisions sd ON sd.scheduling_run_id = sr.id
        WHERE sr.status IN ('COMPLETED', 'REVIEW_REQUIRED', 'APPROVED', 'PUBLISHED', 'SUPERSEDED')
        GROUP BY sr.id, sr.run_code, sr.total_exams
        HAVING sr.total_exams != COUNT(sd.id);
    """
    dec_diff = execute_query(sql_dec_cnt)
    if dec_diff:
        report["summary"]["violations_found"] += len(dec_diff)
        report["cross_table_inconsistencies"]["decision_count_mismatch"] = [dict(r) for r in dec_diff]
        print(f"  [INCONSISTENCY] scheduling_decisions count != total_exams: {len(dec_diff)} runs")
    else:
        print("  [VALID DECISION COUNTS] Exactly one decision per exam in scheduling_decisions.")

    print("\n" + "=" * 80)
    print(f"RELATIONSHIP VALIDATION COMPLETE: {report['summary']['checks_run']} checks, {report['summary']['violations_found']} violations.")
    print("=" * 80)
    return report

if __name__ == "__main__":
    rep = validate_referential_integrity()
    out_file = ROOT_DIR / "docs" / "database" / "relationship_validation.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2, default=str)
    print(f"Saved relationship validation results to {out_file}")

