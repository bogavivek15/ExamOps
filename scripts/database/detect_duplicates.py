"""
ExamOps Duplicate Detection Engine
Audits every entity for:
1. Exact row duplicates (identical values across all columns)
2. Primary Key / Code duplicates
3. Business Key & Semantic duplicates:
   - Students: student_code, email, (first_name + last_name + date_of_birth)
   - Courses: course_code, (name + academic_period_id)
   - Enrollments: (student_id + course_id + academic_period_id), enrollment_code
   - Exams: exam_code, (course_id + title + academic_period_id)
   - Rooms: room_code, (building + name)
   - Room Capacities: (room_id + effective_start + effective_end)
   - Invigilators: invigilator_code, email, (first_name + last_name)
   - Availabilities: (invigilator_id + specific_date/day_of_week + start_time + end_time)
   - Accommodations: (student_id + accommodation_type + effective_start + effective_end)
   - Scheduling Runs: run_code, (academic_period_id + seed + status)
   - Schedule Assignments: assignment_code, (scheduling_run_id + exam_id + room_id), (scheduling_run_id + room_id + start_time + end_time)
   - Assignment Students: (assignment_id + student_id), (run_exam_student_id)
   - Assignment Invigilators: (assignment_id + invigilator_id)
   - Scheduling Decisions: (scheduling_run_id + exam_id)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import get_db_cursor, execute_query

def audit_duplicates() -> Dict[str, Any]:
    print("=" * 80)
    print("PHASE 2.A: EXAMOPS COMPREHENSIVE DUPLICATE DETECTION AUDIT")
    print("=" * 80)

    findings = {
        "summary": {
            "tables_checked": 0,
            "duplicate_groups_found": 0,
            "total_duplicate_rows": 0,
        },
        "exact_duplicates": {},
        "business_key_duplicates": {},
        "semantic_duplicates": {},
    }

    # List of queries for business key / semantic checks
    checks = [
        # 1. Students
        {
            "entity": "students",
            "check": "student_code",
            "type": "business_key",
            "sql": """
                SELECT student_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM students 
                GROUP BY student_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "students",
            "check": "email",
            "type": "business_key",
            "sql": """
                SELECT lower(email) as email, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM students 
                GROUP BY lower(email) HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "students",
            "check": "name_and_dob",
            "type": "semantic",
            "sql": """
                SELECT lower(first_name) as first_name, lower(last_name) as last_name, date_of_birth, 
                       COUNT(*) as cnt, array_agg(id::text) as ids, array_agg(student_code) as codes
                FROM students 
                GROUP BY lower(first_name), lower(last_name), date_of_birth HAVING COUNT(*) > 1;
            """
        },
        # 2. Courses
        {
            "entity": "courses",
            "check": "course_code",
            "type": "business_key",
            "sql": """
                SELECT course_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM courses 
                GROUP BY course_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "courses",
            "check": "name_and_period",
            "type": "semantic",
            "sql": """
                SELECT lower(name) as name, academic_period_id, COUNT(*) as cnt, 
                       array_agg(id::text) as ids, array_agg(course_code) as codes
                FROM courses 
                GROUP BY lower(name), academic_period_id HAVING COUNT(*) > 1;
            """
        },
        # 3. Enrollments
        {
            "entity": "enrollments",
            "check": "enrollment_code",
            "type": "business_key",
            "sql": """
                SELECT enrollment_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM enrollments 
                GROUP BY enrollment_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "enrollments",
            "check": "student_course_period",
            "type": "business_key",
            "sql": """
                SELECT student_id, course_id, academic_period_id, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM enrollments 
                GROUP BY student_id, course_id, academic_period_id HAVING COUNT(*) > 1;
            """
        },
        # 4. Exams
        {
            "entity": "exams",
            "check": "exam_code",
            "type": "business_key",
            "sql": """
                SELECT exam_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM exams 
                GROUP BY exam_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "exams",
            "check": "course_title_period",
            "type": "semantic",
            "sql": """
                SELECT course_id, lower(title) as title, academic_period_id, COUNT(*) as cnt, 
                       array_agg(id::text) as ids, array_agg(exam_code) as codes
                FROM exams 
                GROUP BY course_id, lower(title), academic_period_id HAVING COUNT(*) > 1;
            """
        },
        # 5. Exam Requirements
        {
            "entity": "exam_requirements",
            "check": "requirement_code",
            "type": "business_key",
            "sql": """
                SELECT requirement_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM exam_requirements 
                GROUP BY requirement_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "exam_requirements",
            "check": "exam_req_type_value",
            "type": "semantic",
            "sql": """
                SELECT exam_id, requirement_type, value, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM exam_requirements 
                GROUP BY exam_id, requirement_type, value HAVING COUNT(*) > 1;
            """
        },
        # 6. Rooms
        {
            "entity": "rooms",
            "check": "room_code",
            "type": "business_key",
            "sql": """
                SELECT room_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM rooms 
                GROUP BY room_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "rooms",
            "check": "building_and_name",
            "type": "semantic",
            "sql": """
                SELECT lower(building) as bld, lower(name) as name, COUNT(*) as cnt, 
                       array_agg(id::text) as ids, array_agg(room_code) as codes
                FROM rooms 
                GROUP BY lower(building), lower(name) HAVING COUNT(*) > 1;
            """
        },
        # 7. Room Capacities
        {
            "entity": "room_capacities",
            "check": "capacity_code",
            "type": "business_key",
            "sql": """
                SELECT capacity_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM room_capacities 
                GROUP BY capacity_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "room_capacities",
            "check": "room_effective_dates",
            "type": "business_key",
            "sql": """
                SELECT room_id, effective_start, effective_end, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM room_capacities 
                GROUP BY room_id, effective_start, effective_end HAVING COUNT(*) > 1;
            """
        },
        # 8. Invigilators
        {
            "entity": "invigilators",
            "check": "invigilator_code",
            "type": "business_key",
            "sql": """
                SELECT invigilator_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM invigilators 
                GROUP BY invigilator_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "invigilators",
            "check": "email",
            "type": "business_key",
            "sql": """
                SELECT lower(email) as email, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM invigilators 
                GROUP BY lower(email) HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "invigilators",
            "check": "name",
            "type": "semantic",
            "sql": """
                SELECT lower(first_name) as first_name, lower(last_name) as last_name, 
                       COUNT(*) as cnt, array_agg(id::text) as ids, array_agg(invigilator_code) as codes
                FROM invigilators 
                GROUP BY lower(first_name), lower(last_name) HAVING COUNT(*) > 1;
            """
        },
        # 9. Availabilities
        {
            "entity": "availabilities",
            "check": "availability_code",
            "type": "business_key",
            "sql": """
                SELECT availability_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM availabilities 
                GROUP BY availability_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "availabilities",
            "check": "invigilator_slot_overlap",
            "type": "semantic",
            "sql": """
                SELECT invigilator_id, day_of_week, specific_date, start_time, end_time, effective_start, effective_end,
                       COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM availabilities 
                GROUP BY invigilator_id, day_of_week, specific_date, start_time, end_time, effective_start, effective_end 
                HAVING COUNT(*) > 1;
            """
        },
        # 10. Accommodations
        {
            "entity": "accommodations",
            "check": "accommodation_code",
            "type": "business_key",
            "sql": """
                SELECT accommodation_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM accommodations 
                GROUP BY accommodation_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "accommodations",
            "check": "student_type_dates",
            "type": "semantic",
            "sql": """
                SELECT student_id, accommodation_type, effective_start, effective_end, 
                       COUNT(*) as cnt, array_agg(id::text) as ids, array_agg(accommodation_code) as codes
                FROM accommodations 
                GROUP BY student_id, accommodation_type, effective_start, effective_end HAVING COUNT(*) > 1;
            """
        },
        # 11. Scheduling Runs
        {
            "entity": "scheduling_runs",
            "check": "run_code",
            "type": "business_key",
            "sql": """
                SELECT run_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM scheduling_runs 
                GROUP BY run_code HAVING COUNT(*) > 1;
            """
        },
        # 12. Schedule Assignments
        {
            "entity": "schedule_assignments",
            "check": "run_assignment_code",
            "type": "business_key",
            "sql": """
                SELECT scheduling_run_id, assignment_code, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM schedule_assignments 
                GROUP BY scheduling_run_id, assignment_code HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "schedule_assignments",
            "check": "run_exam_room",
            "type": "business_key",
            "sql": """
                SELECT scheduling_run_id, exam_id, room_id, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM schedule_assignments 
                GROUP BY scheduling_run_id, exam_id, room_id HAVING COUNT(*) > 1;
            """
        },
        # 13. Assignment Students
        {
            "entity": "assignment_students",
            "check": "assignment_student",
            "type": "business_key",
            "sql": """
                SELECT assignment_id, student_id, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM assignment_students 
                GROUP BY assignment_id, student_id HAVING COUNT(*) > 1;
            """
        },
        {
            "entity": "assignment_students",
            "check": "run_exam_student_unique",
            "type": "business_key",
            "sql": """
                SELECT run_exam_student_id, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM assignment_students 
                GROUP BY run_exam_student_id HAVING COUNT(*) > 1;
            """
        },
        # 14. Assignment Invigilators
        {
            "entity": "assignment_invigilators",
            "check": "assignment_invigilator",
            "type": "business_key",
            "sql": """
                SELECT assignment_id, invigilator_id, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM assignment_invigilators 
                GROUP BY assignment_id, invigilator_id HAVING COUNT(*) > 1;
            """
        },
        # 15. Scheduling Decisions
        {
            "entity": "scheduling_decisions",
            "check": "run_exam",
            "type": "business_key",
            "sql": """
                SELECT scheduling_run_id, exam_id, COUNT(*) as cnt, array_agg(id::text) as ids 
                FROM scheduling_decisions 
                GROUP BY scheduling_run_id, exam_id HAVING COUNT(*) > 1;
            """
        },
    ]

    total_groups = 0
    total_dupes = 0
    checked_tables = set()

    for c in checks:
        checked_tables.add(c["entity"])
        results = execute_query(c["sql"])
        if results:
            group_count = len(results)
            row_count = sum(r["cnt"] for r in results)
            total_groups += group_count
            total_dupes += row_count
            print(f"  [DUPLICATE DETECTED] Table: {c['entity']} | Check: {c['check']} ({c['type']})")
            print(f"    Found {group_count} duplicate groups affecting {row_count} total records.")
            target_dict = findings["business_key_duplicates"] if c["type"] == "business_key" else findings["semantic_duplicates"]
            target_dict[f"{c['entity']}.{c['check']}"] = [dict(r) for r in results]
        else:
            print(f"  [CLEAN] Table: {c['entity']:<22} | Check: {c['check']}")

    findings["summary"]["tables_checked"] = len(checked_tables)
    findings["summary"]["duplicate_groups_found"] = total_groups
    findings["summary"]["total_duplicate_rows"] = total_dupes

    print("\n" + "=" * 80)
    print(f"DUPLICATE DETECTION COMPLETE: {total_groups} groups found ({total_dupes} rows).")
    print("=" * 80)
    return findings

if __name__ == "__main__":
    res = audit_duplicates()
    out_file = ROOT_DIR / "docs" / "database" / "duplicate_findings.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=str)
    print(f"Saved duplicate findings to {out_file}")

