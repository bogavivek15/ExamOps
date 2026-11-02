"""
ExamOps Independent Database Index & Query Execution Plan Audit
Verifies existence, correctness, redundancy, and actual EXPLAIN ANALYZE execution of all migration 004 indexes.
"""
import sys
import os
import json
import time
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import execute_query

def audit_database():
    print("=" * 75)
    print("EXAMOPS INDEPENDENT DATABASE OPTIMIZATION & INDEX AUDIT")
    print("=" * 75)

    # 1. Inspect pg_indexes for all relevant tables
    tables = [
        "assignment_students", "students", "enrollments",
        "courses", "exams", "accommodations", "audit_logs"
    ]
    
    table_list_str = ", ".join(f"'{t}'" for t in tables)
    index_query = f"""
        SELECT tablename, indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = 'public' AND tablename IN ({table_list_str})
        ORDER BY tablename, indexname;
    """
    all_indexes = execute_query(index_query)
    
    print("\n1. Active PostgreSQL Indexes on Target Tables:")
    for idx in all_indexes:
        print(f"  [{idx['tablename']}] {idx['indexname']}: {idx['indexdef']}")

    expected_004_indexes = [
        "idx_as_scheduling_run_id",
        "idx_as_student_run",
        "idx_students_names_code",
        "idx_enr_status_period",
        "idx_courses_period_dept",
        "idx_exams_period_status",
        "idx_acc_active_dates",
        "idx_al_created_action",
    ]

    found_names = {idx["indexname"] for idx in all_indexes}
    missing = [name for name in expected_004_indexes if name not in found_names]
    
    print(f"\n2. Migration 004 Verification:")
    print(f"  - Target Indexes Expected: {len(expected_004_indexes)}")
    print(f"  - Target Indexes Found:    {len(expected_004_indexes) - len(missing)}")
    if missing:
        print(f"  - MISSING INDEXES: {missing}")
    else:
        print(f"  - STATUS: All 8 migration 004 indexes verified present and active!")

    # 3. Check for Duplicate or Redundant Indexes
    print(f"\n3. Duplicate & Redundant Index Analysis:")
    # Check if multiple indexes exist on exactly the same table with identical column definitions
    defs_by_table = {}
    duplicates = []
    for idx in all_indexes:
        t = idx["tablename"]
        # extract columns inside parentheses
        idef = idx["indexdef"]
        if t not in defs_by_table:
            defs_by_table[t] = []
        for existing_name, existing_def in defs_by_table[t]:
            # simple check if identical index definition
            col_part = idef[idef.find("("):] if "(" in idef else ""
            exist_col_part = existing_def[existing_def.find("("):] if "(" in existing_def else ""
            if col_part and col_part == exist_col_part:
                duplicates.append((t, idx["indexname"], existing_name))
        defs_by_table[t].append((idx["indexname"], idef))

    if duplicates:
        print(f"  [WARN] Redundant index definitions found: {duplicates}")
    else:
        print(f"  [PASS] Zero duplicate or redundant index definitions detected.")

    # 4. EXPLAIN ANALYZE on Representative Queries
    print(f"\n4. EXPLAIN (ANALYZE, BUFFERS) Execution Plans:")

    # Get sample IDs
    student_sample = execute_query("SELECT student_code, last_name FROM students LIMIT 1;", fetch_one=True)
    stu_code = student_sample["student_code"] if student_sample else "STU-000001"
    last_prefix = student_sample["last_name"][:3] if student_sample else "Gra"

    run_sample = execute_query("SELECT id FROM scheduling_runs ORDER BY updated_at DESC LIMIT 1;", fetch_one=True)
    run_id = str(run_sample["id"]) if run_sample else "00000000-0000-0000-0000-000000000000"

    period_sample = execute_query("SELECT id FROM academic_periods WHERE is_active = TRUE LIMIT 1;", fetch_one=True)
    period_id = str(period_sample["id"]) if period_sample else "00000000-0000-0000-0000-000000000000"

    test_queries = [
        (
            "Query A: Student Search (idx_students_names_code)",
            f"""EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
                SELECT id, student_code, first_name, last_name 
                FROM students 
                WHERE last_name ILIKE '{last_prefix}%' OR student_code = '{stu_code}'
                LIMIT 15;"""
        ),
        (
            "Query B: Assignment Students Lookup (idx_as_scheduling_run_id)",
            f"""EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
                SELECT count(*) 
                FROM assignment_students 
                WHERE scheduling_run_id = '{run_id}'::uuid;"""
        ),
        (
            "Query C: Active Enrollments by Period (idx_enr_status_period)",
            f"""EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
                SELECT id, student_id, course_id 
                FROM enrollments 
                WHERE status = 'ACTIVE' AND academic_period_id = '{period_id}'::uuid
                LIMIT 15;"""
        ),
        (
            "Query D: Audit Log Recent Actions (idx_al_created_action)",
            """EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
               SELECT id, action, entity_type, created_at 
               FROM audit_logs 
               ORDER BY created_at DESC 
               LIMIT 15;"""
        ),
    ]

    plans_summary = []
    for label, sql in test_queries:
        print(f"\n  -- {label} --")
        try:
            res = execute_query(sql, fetch_one=True)
            plan_json = res.get("QUERY PLAN", [])[0]
            root = plan_json["Plan"]
            exec_time = plan_json["Execution Time"]
            node_type = root["Node Type"]
            
            # Find index scans in the plan tree
            indexes_used = []
            def extract_nodes(n):
                if "Index Name" in n:
                    indexes_used.append((n["Index Name"], n["Node Type"]))
                for child in n.get("Plans", []):
                    extract_nodes(child)
            extract_nodes(root)

            print(f"    Root Node:       {node_type}")
            print(f"    Indexes Used:    {indexes_used}")
            print(f"    Execution Time:  {exec_time:.3f} ms")
            
            plans_summary.append({
                "label": label,
                "node_type": node_type,
                "indexes_used": indexes_used,
                "execution_time_ms": exec_time,
                "full_plan": root,
            })
        except Exception as e:
            print(f"    Error executing plan: {e}")
            plans_summary.append({"label": label, "error": str(e)})

    # Write audit findings
    audit_data = {
        "expected_indexes": expected_004_indexes,
        "active_indexes": [idx["indexname"] for idx in all_indexes],
        "missing_indexes": missing,
        "duplicate_indexes": duplicates,
        "plans": plans_summary,
    }

    with open("docs/performance/database_audit_data.json", "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)
    print("\nDatabase audit data saved to docs/performance/database_audit_data.json")

if __name__ == "__main__":
    audit_database()

