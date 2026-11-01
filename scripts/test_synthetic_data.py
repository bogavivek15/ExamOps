"""
ExamOps Synthetic Data Verification Suite
Tests:
1. Deterministic reproducibility across independent generation runs.
2. Referential integrity and foreign key validity across all records.
3. Regex format compliance for canonical identifiers.
4. Database load & row count reconciliation against PostgreSQL.
"""
import sys
import os
import json
import re
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from generator.generate import generate_dataset
from generator.exporters import export_all, get_canonical_json_hash

def main():
    print("=== Step 1: Testing Reproducibility across Independent Runs ===")
    dataset_1, gt_1 = generate_dataset(profile_name="full", seed=20261022)
    dataset_2, gt_2 = generate_dataset(profile_name="full", seed=20261022)

    assert len(dataset_1) == len(dataset_2), "Entity dictionary length mismatch!"
    for entity in dataset_1:
        hash_1 = get_canonical_json_hash(dataset_1[entity])
        hash_2 = get_canonical_json_hash(dataset_2[entity])
        assert hash_1 == hash_2, f"Hash mismatch for {entity}: {hash_1} != {hash_2}"
        assert len(dataset_1[entity]) == len(dataset_2[entity]), f"Row count mismatch for {entity}"
        print(f"  ✓ {entity}: {len(dataset_1[entity])} rows, SHA-256: {hash_1[:16]}... (Reproducibility 100% MATCH)")

    gt_hash_1 = get_canonical_json_hash(gt_1)
    gt_hash_2 = get_canonical_json_hash(gt_2)
    assert gt_hash_1 == gt_hash_2, "Ground truth hash mismatch!"
    print(f"  ✓ ground_truth: {len(gt_1)} negative fixtures MATCH.")

    print("\n=== Step 2: In-Memory Referential Integrity Verification ===")
    student_ids = {s["id"] for s in dataset_1["students"]}
    course_ids = {c["id"] for c in dataset_1["courses"]}
    period_ids = {p["id"] for p in dataset_1["academic_periods"]}
    exam_ids = {e["id"] for e in dataset_1["exams"]}
    room_ids = {r["id"] for r in dataset_1["rooms"]}
    inv_ids = {i["id"] for i in dataset_1["invigilators"]}
    eq_type_ids = {eq["id"] for eq in dataset_1["equipment_types"]}
    acc_ids = {a["id"] for a in dataset_1["accommodations"]}

    # Verify enrollments
    for enr in dataset_1["enrollments"]:
        assert enr["student_id"] in student_ids, f"Dangling student_id in {enr}"
        assert enr["course_id"] in course_ids, f"Dangling course_id in {enr}"
        assert enr["academic_period_id"] in period_ids, f"Dangling period_id in {enr}"
    print(f"  ✓ All {len(dataset_1['enrollments'])} enrollments reference valid students and courses.")

    # Verify exams
    for ex in dataset_1["exams"]:
        assert ex["course_id"] in course_ids, f"Dangling course_id in {ex}"
        assert ex["academic_period_id"] in period_ids, f"Dangling period_id in {ex}"
    print(f"  ✓ All {len(dataset_1['exams'])} exams reference valid courses and academic periods.")

    # Verify exam requirements
    for req in dataset_1["exam_requirements"]:
        assert req["exam_id"] in exam_ids, f"Dangling exam_id in {req}"
    print(f"  ✓ All {len(dataset_1['exam_requirements'])} requirements reference valid exams.")

    # Verify room capacities and equipment
    for rc in dataset_1["room_capacities"]:
        assert rc["room_id"] in room_ids, f"Dangling room_id in {rc}"
    for re_item in dataset_1["room_equipment"]:
        assert re_item["room_id"] in room_ids, f"Dangling room_id in {re_item}"
        assert re_item["equipment_type_id"] in eq_type_ids, f"Dangling eq_id in {re_item}"
    print(f"  ✓ All room capacities and equipment reference valid rooms and equipment types.")

    # Verify availabilities
    for ra in dataset_1["room_availabilities"]:
        assert ra["room_id"] in room_ids, f"Dangling room_id in {ra}"
    for av in dataset_1["availabilities"]:
        assert av["invigilator_id"] in inv_ids, f"Dangling invigilator_id in {av}"
    print(f"  ✓ All room and invigilator availabilities reference valid parents.")

    # Verify accommodations & notes
    for acc in dataset_1["accommodations"]:
        assert acc["student_id"] in student_ids, f"Dangling student_id in {acc}"
    for note in dataset_1["accommodation_notes"]:
        assert note["accommodation_id"] in acc_ids, f"Dangling accommodation_id in {note}"
    print(f"  ✓ All accommodations and confidential notes reference valid parents.")

    print("\n=== Step 3: Identifier Format Verification ===")
    stu_regex = re.compile(r"^STU-[0-9]{6}$")
    for s in dataset_1["students"]:
        assert stu_regex.match(s["student_code"]), f"Bad student code format: {s['student_code']}"

    exam_regex = re.compile(r"^EXAM-[0-9]{4}-[0-9]{6}$")
    for e in dataset_1["exams"]:
        assert exam_regex.match(e["exam_code"]), f"Bad exam code format: {e['exam_code']}"

    room_regex = re.compile(r"^ROOM-[0-9]{6}$")
    for r in dataset_1["rooms"]:
        assert room_regex.match(r["room_code"]), f"Bad room code format: {r['room_code']}"

    inv_regex = re.compile(r"^INV-[0-9]{6}$")
    for i in dataset_1["invigilators"]:
        assert inv_regex.match(i["invigilator_code"]), f"Bad invigilator code format: {i['invigilator_code']}"
    print("  ✓ All identifiers strictly conform to canonical uppercase padded syntax.")

    print("\n=== Step 4: Loading SQL Seed into PostgreSQL & Reconciling Counts ===")
    # Clean reset of database schema and re-application of migrations
    import glob
    clean_sql = """
    DROP SCHEMA IF EXISTS public CASCADE;
    CREATE SCHEMA public;
    GRANT ALL ON SCHEMA public TO postgres;
    GRANT ALL ON SCHEMA public TO public;
    CREATE SCHEMA IF NOT EXISTS auth;
    CREATE OR REPLACE FUNCTION auth.uid() 
    RETURNS UUID 
    LANGUAGE sql 
    STABLE 
    AS $$ 
        SELECT nullif(current_setting('request.jwt.claim.sub', true), '')::uuid; 
    $$;
    """
    subprocess.run(
        ["docker", "exec", "-i", "examops-db-test", "psql", "-U", "postgres", "-d", "examops", "-v", "ON_ERROR_STOP=1"],
        input=clean_sql, text=True, check=True
    )
    for mf in sorted(glob.glob("supabase/migrations/*.sql")):
        with open(mf, encoding="utf-8") as f:
            msql = f.read()
        subprocess.run(
            ["docker", "exec", "-i", "examops-db-test", "psql", "-U", "postgres", "-d", "examops", "-v", "ON_ERROR_STOP=1"],
            input=msql, text=True, check=True
        )

    # Load data/sql/seed_data.sql into PostgreSQL container
    seed_file_path = os.path.join("data", "sql", "seed_data.sql")
    print(f"Loading '{seed_file_path}' into container 'examops-db-test'...")
    with open(seed_file_path, "r", encoding="utf-8") as f:
        seed_sql = f.read()

    res = subprocess.run(
        ["docker", "exec", "-i", "examops-db-test", "psql", "-U", "postgres", "-d", "examops", "-v", "ON_ERROR_STOP=1"],
        input=seed_sql,
        text=True,
        capture_output=True
    )
    if res.returncode != 0:
        print("SQL Seed Load Error STDERR:\n", res.stderr)
        sys.exit(1)
    print("SQL Seed loaded cleanly without errors!")

    # Reconcile counts in PostgreSQL
    print("\nReconciling PostgreSQL table counts against generated source counts:")
    for entity in [
        "academic_periods", "students", "invigilators", "user_profiles", "courses",
        "course_instructors", "enrollments", "exams", "exam_requirements", "rooms",
        "room_capacities", "equipment_types", "room_equipment", "room_availabilities",
        "availabilities", "accommodations", "accommodation_notes"
    ]:
        count_query = f"SELECT count(*) FROM {entity};"
        q_res = subprocess.run(
            ["docker", "exec", "-i", "examops-db-test", "psql", "-U", "postgres", "-d", "examops", "-t", "-A"],
            input=count_query,
            text=True,
            capture_output=True
        )
        db_count = int(q_res.stdout.strip())
        src_count = len(dataset_1[entity])
        assert db_count == src_count, f"Count mismatch for {entity}: DB={db_count}, Source={src_count}"
        print(f"  ✓ {entity:22s} | Source: {src_count:6d} | DB: {db_count:6d} | STATUS: RECONCILED")

    print("\n==================================================================")
    print("ALL PHASE 2 SYNTHETIC DATA VERIFICATIONS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    main()
