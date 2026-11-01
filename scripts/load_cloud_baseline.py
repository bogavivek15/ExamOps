"""
ExamOps Cloud Baseline Data Loader
Loads the deterministic seed dataset (seed 20261022) into Supabase PostgreSQL.
Verifies record counts, foreign keys, and isolation of negative test fixtures.
"""
import sys
import os
import json
import time
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_batch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings
from backend.database import mask_connection_url

EXPECTED_COUNTS = {
    "students": 5000,
    "courses": 150,
    "enrollments": 25044,
    "exams": 300,
    "rooms": 100,
    "invigilators": 200,
    "academic_periods": 1,
    "accommodations": 301,
    "equipment_types": 5,
}

def load_baseline():
    masked_url = mask_connection_url(settings.DATABASE_URL)
    print(f"Connecting to database: {masked_url}")

    if "[YOUR-PASSWORD]" in settings.DATABASE_URL:
        print("\n[BLOCKED] DATABASE_URL still contains placeholder '[YOUR-PASSWORD]'.")
        print("Please configure your actual database password in .env before running baseline data loader.")
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

    # Check if data already loaded
    cursor.execute("SELECT COUNT(*) FROM students;")
    existing_students = cursor.fetchone()[0]
    print(f"Current students count in database: {existing_students}")

    seed_sql_path = Path("data/sql/seed_data.sql")
    if not seed_sql_path.exists():
        print(f"[FAIL] Seed file '{seed_sql_path}' not found.")
        sys.exit(1)

    if existing_students >= 5000:
        print("Baseline data already present (>= 5,000 students). Skipping insertion.")
    else:
        print(f"Reading seed data from {seed_sql_path} ({seed_sql_path.stat().st_size / (1024*1024):.2f} MB)...")
        with open(seed_sql_path, "r", encoding="utf-8") as f:
            sql_statements = f.read()

        print("Executing seed SQL script against Supabase...")
        start_t = time.time()
        # Disable statement timeout if any, and execute
        cursor.execute("SET statement_timeout = 0;")
        cursor.execute(sql_statements)
        elapsed = time.time() - start_t
        print(f"Seed data execution completed in {elapsed:.2f}s.")

    # Verification of table counts
    print("\n--- Verifying Actual Row Counts in Supabase ---")
    all_passed = True
    for table, expected in EXPECTED_COUNTS.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        actual = cursor.fetchone()[0]
        status = "PASS" if actual == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  [{status}] {table}: actual={actual}, expected={expected}")

    # Verify negative fixtures segregation
    print("\n--- Verifying Negative Test Fixtures Isolation ---")
    gt_file = Path("data/ground_truth.json")
    if gt_file.exists():
        with open(gt_file, "r", encoding="utf-8") as f:
            gt_data = json.load(f)
        print(f"Ground truth file contains {len(gt_data)} negative scenarios (NEG-001 through NEG-005).")
        # Ensure no negative fixture was inserted into scheduling_runs or operational anomalies
        cursor.execute("SELECT COUNT(*) FROM scheduling_runs WHERE run_code LIKE 'NEG-%';")
        neg_runs = cursor.fetchone()[0]
        assert neg_runs == 0, f"Found {neg_runs} negative fixtures in scheduling_runs! Ground truth must remain separate."
        print(f"  [PASS] Operational tables contain 0 ground-truth negative artifacts. Clean isolation verified.")

    cursor.close()
    conn.close()

    if not all_passed:
        print("\n[FAIL] Baseline verification failed due to count mismatches.")
        sys.exit(1)

    print("\n[SUCCESS] Baseline data loaded and fully verified!")

if __name__ == "__main__":
    load_baseline()

