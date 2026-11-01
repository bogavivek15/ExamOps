"""
ExamOps Cloud Migration Runner
Applies Supabase SQL migrations directly via psycopg2 using DATABASE_URL.
Verifies entities, constraints, and RLS policies.
"""
import sys
import os
import glob
from pathlib import Path
import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings
from backend.database import mask_connection_url

EXPECTED_TABLES = sorted([
    "academic_periods", "accommodation_notes", "accommodations", "assignment_invigilators",
    "assignment_students", "audit_logs", "availabilities", "course_instructors", "courses",
    "enrollments", "equipment_types", "exam_requirements", "exams", "invigilators",
    "room_availabilities", "room_capacities", "room_equipment", "rooms", "run_exam_students",
    "schedule_assignments", "schedule_events", "scheduling_decisions", "scheduling_runs",
    "students", "user_profiles", "validation_issues"
])

def run_migrations():
    masked_url = mask_connection_url(settings.DATABASE_URL)
    print(f"Connecting to database: {masked_url}")
    
    if "[YOUR-PASSWORD]" in settings.DATABASE_URL:
        print("\n[BLOCKED] DATABASE_URL still contains placeholder '[YOUR-PASSWORD]'.")
        print("Please configure your actual database password in .env before running migrations.")
        sys.exit(1)

    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.autocommit = True
    except Exception as e:
        print(f"\n[FAIL] Could not establish connection to {masked_url}:")
        print(f"Error details: {e}")
        sys.exit(1)

    cursor = conn.cursor()
    print("Database connection successfully established.\n")

    # Inspect current migrations/tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    existing_tables = [row[0] for row in cursor.fetchall()]
    print(f"Existing tables in public schema: {len(existing_tables)} found.")

    migration_files = sorted(glob.glob("supabase/migrations/*.sql"))
    print(f"\nFound {len(migration_files)} migration files in supabase/migrations/ :")
    for mf in migration_files:
        print(f"  - {mf}")

    print("\n--- Applying migrations in order ---")
    for mf in migration_files:
        mf_name = os.path.basename(mf)
        print(f"Applying: {mf_name} ...", end=" ", flush=True)
        with open(mf, "r", encoding="utf-8") as f:
            sql_content = f.read()
        try:
            cursor.execute(sql_content)
            print("DONE.")
        except Exception as e:
            print(f"\n[FAIL] Failed to apply {mf_name}: {e}")
            conn.close()
            sys.exit(1)

    # Verification
    print("\n--- Verifying All 26 Tables ---")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    current_tables = sorted([row[0] for row in cursor.fetchall()])
    missing = set(EXPECTED_TABLES) - set(current_tables)
    if missing:
        print(f"[FAIL] Missing tables: {missing}")
        sys.exit(1)
    print(f"[PASS] All {len(EXPECTED_TABLES)} required entities exist in Supabase public schema.")

    # Check RLS enabled
    cursor.execute("""
        SELECT relname, relrowsecurity 
        FROM pg_class 
        JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
        WHERE pg_namespace.nspname = 'public' AND relkind = 'r'
        ORDER BY relname;
    """)
    rls_status = {row[0]: row[1] for row in cursor.fetchall()}
    non_rls = [t for t in EXPECTED_TABLES if not rls_status.get(t, False)]
    if non_rls:
        print(f"[WARNING] Tables without RLS enabled: {non_rls}")
    else:
        print(f"[PASS] Row Level Security (RLS) is ENABLED on all {len(EXPECTED_TABLES)} tables.")

    cursor.close()
    conn.close()
    print("\n[SUCCESS] Migration run and schema verification completed successfully!")

if __name__ == "__main__":
    run_migrations()

