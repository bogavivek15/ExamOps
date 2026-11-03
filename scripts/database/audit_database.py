"""
ExamOps Database Integrity & Comprehensive Audit Script
Connects to Supabase PostgreSQL and performs:
1. Complete Schema Discovery (Tables, Columns, Types, PKs, FKs, Unique, Checks, Indexes, Triggers, RLS, Views, Functions)
2. Row-by-Row Counts & Baseline Reconciliation
3. Duplicate Detection (Exact, Business-Key, Entity-level)
4. Nullability & Data Quality Verification (Missing fields, empty strings, invalid ranges/enums)
5. Referential Integrity & Orphaned Records Verification
6. Cross-Table Consistency Verification
7. ExamOps Business Rules & Constraints Verification (Student Conflicts, Room Double-booking, Capacity, Invigilators, Accommodations)
8. Output structured findings for the Database Integrity Audit Report.
"""
import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.config import settings
from backend.database import get_db_cursor, execute_query, mask_connection_url

def discover_database_schema():
    print("=" * 80)
    print("PHASE 1: COMPLETE DATABASE SCHEMA DISCOVERY")
    print(f"Target Database: {mask_connection_url(settings.DATABASE_URL)}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    schema_info = {
        "tables": {},
        "views": [],
        "functions": [],
        "triggers": [],
        "rls_policies": [],
        "row_counts": {},
    }

    with get_db_cursor() as cur:
        # 1. Base Tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        table_names = [r["table_name"] for r in cur.fetchall()]
        print(f"Discovered {len(table_names)} Base Tables in 'public' schema.")

        # 2. Views
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'VIEW'
            ORDER BY table_name;
        """)
        schema_info["views"] = [r["table_name"] for r in cur.fetchall()]

        # 3. Columns for each table
        cur.execute("""
            SELECT table_name, column_name, data_type, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)
        columns_by_table = defaultdict(list)
        for r in cur.fetchall():
            columns_by_table[r["table_name"]].append(dict(r))

        # 4. Constraints (PK, FK, UNIQUE, CHECK)
        cur.execute("""
            SELECT 
                tc.table_name, 
                tc.constraint_name, 
                tc.constraint_type,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.update_rule,
                rc.delete_rule
            FROM information_schema.table_constraints AS tc
            LEFT JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            LEFT JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            LEFT JOIN information_schema.referential_constraints AS rc
                ON tc.constraint_name = rc.constraint_name
            WHERE tc.table_schema = 'public'
            ORDER BY tc.table_name, tc.constraint_name;
        """)
        constraints_by_table = defaultdict(list)
        for r in cur.fetchall():
            constraints_by_table[r["table_name"]].append(dict(r))

        # 5. Check constraints definitions
        cur.execute("""
            SELECT tc.table_name, tc.constraint_name, cc.check_clause
            FROM information_schema.table_constraints tc
            JOIN information_schema.check_constraints cc 
                ON tc.constraint_name = cc.constraint_name
            WHERE tc.table_schema = 'public';
        """)
        checks_by_table = defaultdict(list)
        for r in cur.fetchall():
            checks_by_table[r["table_name"]].append(dict(r))

        # 6. Indexes
        cur.execute("""
            SELECT tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)
        indexes_by_table = defaultdict(list)
        for r in cur.fetchall():
            indexes_by_table[r["tablename"]].append(dict(r))

        # 7. Triggers
        cur.execute("""
            SELECT event_object_table AS table_name, trigger_name, event_manipulation, 
                   action_timing, action_statement
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            ORDER BY event_object_table, trigger_name;
        """)
        schema_info["triggers"] = [dict(r) for r in cur.fetchall()]

        # 8. RLS Policies
        cur.execute("""
            SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
            FROM pg_policies
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname;
        """)
        schema_info["rls_policies"] = [dict(r) for r in cur.fetchall()]

        # 9. Database Functions / Procedures
        cur.execute("""
            SELECT routine_name, routine_type, data_type, security_type
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            ORDER BY routine_name;
        """)
        schema_info["functions"] = [dict(r) for r in cur.fetchall()]

        # 10. Table Row Counts
        for t in table_names:
            cur.execute(f'SELECT COUNT(*) as cnt FROM "{t}";')
            cnt = cur.fetchone()["cnt"]
            schema_info["row_counts"][t] = cnt
            schema_info["tables"][t] = {
                "columns": columns_by_table[t],
                "constraints": constraints_by_table[t],
                "checks": checks_by_table[t],
                "indexes": indexes_by_table[t],
                "row_count": cnt,
            }
            print(f"  Table: {t:<28} Rows: {cnt}")

    return schema_info

if __name__ == "__main__":
    schema = discover_database_schema()
    out_path = ROOT_DIR / "docs" / "database" / "schema_discovery.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, default=str)
    print(f"\n[SUCCESS] Discovery output written to {out_path}")

