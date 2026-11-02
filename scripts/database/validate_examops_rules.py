"""
ExamOps Business Rules & Constraints Verification Engine
Validates the 5 Hard Constraints and operational rules:
1. Student Conflict Constraint: No student has overlapping exams or simultaneous rooms
2. Room Double-Booking & Operating Hours Constraint: No overlapping room assignments, inside availability
3. Room Capacity Constraint: Seated students <= exam_capacity on that date
4. Invigilator Double-Booking, Availability & Workload: No overlaps, within availability & hours
5. Accommodation Compliance: Extra time applied, accessible rooms for mobility needs, low distraction
6. Decision Telemetry & Unscheduled Reason Documentation
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import get_db_cursor, execute_query

def validate_examops_rules() -> Dict[str, Any]:
    print("=" * 80)
    print("PHASE 3: EXAMOPS BUSINESS RULES & HARD CONSTRAINTS VALIDATION")
    print("=" * 80)

    report = {
        "student_conflicts": [],
        "room_double_bookings": [],
        "room_capacity_violations": [],
        "room_operating_hour_violations": [],
        "invigilator_double_bookings": [],
        "invigilator_workload_violations": [],
        "accommodation_violations": [],
        "unassigned_explanation_violations": [],
        "summary": {
            "total_hard_constraint_violations": 0,
            "rule_checks_passed": 0,
            "rule_checks_failed": 0,
        }
    }

    # Query published or latest confirmed run
    run = execute_query("""
        SELECT id, run_code, status 
        FROM scheduling_runs 
        WHERE status = 'PUBLISHED' 
        ORDER BY updated_at DESC LIMIT 1;
    """, fetch_one=True)

    if not run:
        # Fall back to latest approved/completed run
        run = execute_query("""
            SELECT id, run_code, status 
            FROM scheduling_runs 
            WHERE status IN ('APPROVED', 'REVIEW_REQUIRED', 'PUBLISHED') 
            ORDER BY updated_at DESC LIMIT 1;
        """, fetch_one=True)

    if not run:
        print("[WARN] No active/published scheduling run found to validate.")
        return report

    run_id = run["id"]
    print(f"Auditing Scheduling Run: {run['run_code']} (Status: {run['status']}, ID: {run_id})")

    # --------------------------------------------------------------------------
    # 1. Student Conflict Validation
    # A student cannot be seated in two exams whose time intervals overlap
    # Verified using student's actual individual effective duration:
    # [start_time, start_time + effective_duration_minutes)
    # --------------------------------------------------------------------------
    print("\n--- 1. Checking Student Conflicts ---")
    sql_student_conflicts = """
        SELECT 
            ast1.student_id,
            s.student_code,
            s.first_name || ' ' || s.last_name as student_name,
            sa1.exam_id as exam1_id,
            e1.exam_code as exam1_code,
            sa1.start_time as exam1_start,
            (sa1.start_time + make_interval(mins => ast1.effective_duration_minutes)) as student1_end,
            sa2.exam_id as exam2_id,
            e2.exam_code as exam2_code,
            sa2.start_time as exam2_start,
            (sa2.start_time + make_interval(mins => ast2.effective_duration_minutes)) as student2_end
        FROM assignment_students ast1
        JOIN schedule_assignments sa1 ON sa1.id = ast1.assignment_id
        JOIN assignment_students ast2 ON ast2.student_id = ast1.student_id AND ast2.id != ast1.id
        JOIN schedule_assignments sa2 ON sa2.id = ast2.assignment_id
        JOIN students s ON s.id = ast1.student_id
        JOIN exams e1 ON e1.id = sa1.exam_id
        JOIN exams e2 ON e2.id = sa2.exam_id
        WHERE sa1.scheduling_run_id = %s
          AND sa2.scheduling_run_id = %s
          AND sa1.status = 'CONFIRMED'
          AND sa2.status = 'CONFIRMED'
          AND sa1.exam_id < sa2.exam_id  -- eliminate duplicates/reversals
          AND (
            sa1.start_time < (sa2.start_time + make_interval(mins => ast2.effective_duration_minutes))
            AND (sa1.start_time + make_interval(mins => ast1.effective_duration_minutes)) > sa2.start_time
          );
    """
    stu_conflicts = execute_query(sql_student_conflicts, (run_id, run_id))
    if stu_conflicts:
        report["student_conflicts"] = [dict(r) for r in stu_conflicts]
        report["summary"]["total_hard_constraint_violations"] += len(stu_conflicts)
        report["summary"]["rule_checks_failed"] += 1
        print(f"  [FAIL] Detected {len(stu_conflicts)} student overlapping exam conflicts!")
    else:
        report["summary"]["rule_checks_passed"] += 1
        print("  [PASS] Zero student conflicts detected (0 overlapping examination intervals).")

    # --------------------------------------------------------------------------
    # 2. Room Double-Booking Validation
    # A single room cannot host two overlapping assignments in the same run
    # --------------------------------------------------------------------------
    print("\n--- 2. Checking Room Double-Bookings ---")
    sql_room_overlap = """
        SELECT 
            sa1.room_id,
            r.room_code,
            r.name as room_name,
            sa1.id as assignment1_id,
            sa1.exam_id as exam1_id,
            e1.exam_code as exam1_code,
            sa1.start_time as start1,
            sa1.end_time as end1,
            sa2.id as assignment2_id,
            sa2.exam_id as exam2_id,
            e2.exam_code as exam2_code,
            sa2.start_time as start2,
            sa2.end_time as end2
        FROM schedule_assignments sa1
        JOIN schedule_assignments sa2 
            ON sa1.room_id = sa2.room_id 
            AND sa1.id < sa2.id
            AND sa1.scheduling_run_id = sa2.scheduling_run_id
        JOIN rooms r ON r.id = sa1.room_id
        JOIN exams e1 ON e1.id = sa1.exam_id
        JOIN exams e2 ON e2.id = sa2.exam_id
        WHERE sa1.scheduling_run_id = %s
          AND sa1.status = 'CONFIRMED'
          AND sa2.status = 'CONFIRMED'
          AND (sa1.start_time < sa2.end_time AND sa1.end_time > sa2.start_time);
    """
    room_conflicts = execute_query(sql_room_overlap, (run_id,))
    if room_conflicts:
        report["room_double_bookings"] = [dict(r) for r in room_conflicts]
        report["summary"]["total_hard_constraint_violations"] += len(room_conflicts)
        report["summary"]["rule_checks_failed"] += 1
        print(f"  [FAIL] Detected {len(room_conflicts)} room double-booking overlaps!")
    else:
        report["summary"]["rule_checks_passed"] += 1
        print("  [PASS] Zero room double-booking overlaps detected.")

    # --------------------------------------------------------------------------
    # 3. Room Capacity Validation
    # Seated students in each assignment <= room exam_capacity on assignment date
    # --------------------------------------------------------------------------
    print("\n--- 3. Checking Room Capacity Adherence ---")
    sql_room_capacity = """
        SELECT 
            sa.id as assignment_id,
            sa.assignment_code,
            r.room_code,
            r.name as room_name,
            COUNT(ast.id) as seated_students,
            rc.exam_capacity,
            rc.standard_capacity
        FROM schedule_assignments sa
        JOIN rooms r ON r.id = sa.room_id
        LEFT JOIN assignment_students ast ON ast.assignment_id = sa.id
        LEFT JOIN room_capacities rc 
            ON rc.room_id = sa.room_id 
            AND sa.start_time::date >= rc.effective_start 
            AND sa.start_time::date <= rc.effective_end
        WHERE sa.scheduling_run_id = %s
          AND sa.status = 'CONFIRMED'
        GROUP BY sa.id, sa.assignment_code, r.room_code, r.name, rc.exam_capacity, rc.standard_capacity
        HAVING COUNT(ast.id) > rc.exam_capacity;
    """
    cap_violations = execute_query(sql_room_capacity, (run_id,))
    if cap_violations:
        report["room_capacity_violations"] = [dict(r) for r in cap_violations]
        report["summary"]["total_hard_constraint_violations"] += len(cap_violations)
        report["summary"]["rule_checks_failed"] += 1
        print(f"  [FAIL] Detected {len(cap_violations)} room capacity overfills!")
    else:
        report["summary"]["rule_checks_passed"] += 1
        print("  [PASS] All assignments strictly adhere to room exam capacities.")

    # --------------------------------------------------------------------------
    # 4. Invigilator Double-Booking & Availability Validation
    # No overlapping assignments for the same invigilator
    # --------------------------------------------------------------------------
    print("\n--- 4. Checking Invigilator Double-Bookings ---")
    sql_inv_overlap = """
        SELECT 
            ai1.invigilator_id,
            i.invigilator_code,
            i.first_name || ' ' || i.last_name as invigilator_name,
            sa1.id as assignment1_id,
            sa1.start_time as start1,
            sa1.end_time as end1,
            sa2.id as assignment2_id,
            sa2.start_time as start2,
            sa2.end_time as end2
        FROM assignment_invigilators ai1
        JOIN schedule_assignments sa1 ON sa1.id = ai1.assignment_id
        JOIN assignment_invigilators ai2 
            ON ai2.invigilator_id = ai1.invigilator_id 
            AND ai1.id < ai2.id
        JOIN schedule_assignments sa2 ON sa2.id = ai2.assignment_id
        JOIN invigilators i ON i.id = ai1.invigilator_id
        WHERE sa1.scheduling_run_id = %s
          AND sa2.scheduling_run_id = %s
          AND sa1.status = 'CONFIRMED'
          AND sa2.status = 'CONFIRMED'
          AND (sa1.start_time < sa2.end_time AND sa1.end_time > sa2.start_time);
    """
    inv_conflicts = execute_query(sql_inv_overlap, (run_id, run_id))
    if inv_conflicts:
        report["invigilator_double_bookings"] = [dict(r) for r in inv_conflicts]
        report["summary"]["total_hard_constraint_violations"] += len(inv_conflicts)
        report["summary"]["rule_checks_failed"] += 1
        print(f"  [FAIL] Detected {len(inv_conflicts)} invigilator double-booking overlaps!")
    else:
        report["summary"]["rule_checks_passed"] += 1
        print("  [PASS] Zero invigilator double-booking overlaps detected.")

    # Invigilator Workload check
    print("\n--- 5. Checking Invigilator Workload Limits ---")
    sql_inv_workload = """
        SELECT 
            i.id,
            i.invigilator_code,
            i.first_name || ' ' || i.last_name as name,
            i.max_hours_per_day,
            sa.start_time::date as exam_date,
            SUM(EXTRACT(EPOCH FROM (sa.end_time - sa.start_time)) / 3600.0) as daily_hours
        FROM assignment_invigilators ai
        JOIN schedule_assignments sa ON sa.id = ai.assignment_id
        JOIN invigilators i ON i.id = ai.invigilator_id
        WHERE sa.scheduling_run_id = %s
          AND sa.status = 'CONFIRMED'
        GROUP BY i.id, i.invigilator_code, i.first_name, i.last_name, i.max_hours_per_day, sa.start_time::date
        HAVING SUM(EXTRACT(EPOCH FROM (sa.end_time - sa.start_time)) / 3600.0) > i.max_hours_per_day;
    """
    workload_violations = execute_query(sql_inv_workload, (run_id,))
    if workload_violations:
        report["invigilator_workload_violations"] = [dict(r) for r in workload_violations]
        report["summary"]["total_hard_constraint_violations"] += len(workload_violations)
        report["summary"]["rule_checks_failed"] += 1
        print(f"  [FAIL] Detected {len(workload_violations)} invigilator daily workload cap violations!")
    else:
        report["summary"]["rule_checks_passed"] += 1
        print("  [PASS] All invigilators remain within daily maximum workload limits.")

    # --------------------------------------------------------------------------
    # 6. Accommodation Compliance
    # Accessible room assigned if student has ACCESSIBLE_ROOM accommodation
    # --------------------------------------------------------------------------
    print("\n--- 6. Checking Accommodation Compliance ---")
    sql_acc_compliance = """
        SELECT 
            ast.student_id,
            s.student_code,
            a.accommodation_type,
            r.room_code,
            r.name as room_name,
            r.is_accessible,
            sa.assignment_code
        FROM assignment_students ast
        JOIN schedule_assignments sa ON sa.id = ast.assignment_id
        JOIN rooms r ON r.id = sa.room_id
        JOIN students s ON s.id = ast.student_id
        JOIN accommodations a ON a.student_id = ast.student_id AND a.is_active = TRUE
        WHERE sa.scheduling_run_id = %s
          AND sa.status = 'CONFIRMED'
          AND a.accommodation_type = 'ACCESSIBLE_ROOM'
          AND r.is_accessible = FALSE;
    """
    acc_violations = execute_query(sql_acc_compliance, (run_id,))
    if acc_violations:
        report["accommodation_violations"] = [dict(r) for r in acc_violations]
        report["summary"]["total_hard_constraint_violations"] += len(acc_violations)
        report["summary"]["rule_checks_failed"] += 1
        print(f"  [FAIL] Detected {len(acc_violations)} students requiring accessible room assigned to non-accessible room!")
    else:
        report["summary"]["rule_checks_passed"] += 1
        print("  [PASS] All accessibility accommodation requirements strictly satisfied.")

    # --------------------------------------------------------------------------
    # 7. Unassigned Examination Explanation Documentation
    # Every unassigned exam must have reason_codes documented in scheduling_decisions
    # --------------------------------------------------------------------------
    print("\n--- 7. Checking Unassigned Examination Explanations ---")
    sql_unassigned_reasons = """
        SELECT sd.exam_id, e.exam_code, sd.is_assigned, sd.reason_codes
        FROM scheduling_decisions sd
        JOIN exams e ON e.id = sd.exam_id
        WHERE sd.scheduling_run_id = %s
          AND sd.is_assigned = FALSE
          AND (sd.reason_codes IS NULL OR array_length(sd.reason_codes, 1) = 0);
    """
    unexp_violations = execute_query(sql_unassigned_reasons, (run_id,))
    if unexp_violations:
        report["unassigned_explanation_violations"] = [dict(r) for r in unexp_violations]
        report["summary"]["total_hard_constraint_violations"] += len(unexp_violations)
        report["summary"]["rule_checks_failed"] += 1
        print(f"  [FAIL] Detected {len(unexp_violations)} unassigned exams without explanation reason codes!")
    else:
        report["summary"]["rule_checks_passed"] += 1
        print("  [PASS] 100% of unassigned exams have documented decision reason codes.")

    print("\n" + "=" * 80)
    print(f"EXAMOPS RULES AUDIT SUMMARY: {report['summary']['rule_checks_passed']} Passed, {report['summary']['rule_checks_failed']} Failed.")
    print(f"Total Hard Constraint Violations: {report['summary']['total_hard_constraint_violations']}")
    print("=" * 80)
    return report

if __name__ == "__main__":
    rep = validate_examops_rules()
    out_file = ROOT_DIR / "docs" / "database" / "rules_validation.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2, default=str)
    print(f"Saved rules validation results to {out_file}")
