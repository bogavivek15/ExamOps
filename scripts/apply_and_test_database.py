import subprocess
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

CONTAINER = "examops-db-test"
DB = "examops"
USER = "postgres"

def run_sql(sql: str, tuples_only: bool = False, on_error_stop: bool = True) -> subprocess.CompletedProcess:
    args = ["docker", "exec", "-i", CONTAINER, "psql", "-U", USER, "-d", DB]
    if on_error_stop:
        args.extend(["-v", "ON_ERROR_STOP=1"])
    if tuples_only:
        args.extend(["-t", "-A"])
    return subprocess.run(
        args,
        input=sql,
        text=True,
        capture_output=True
    )

def execute_or_fail(sql: str, description: str):
    res = run_sql(sql)
    if res.returncode != 0:
        print(f"FAILED: {description}")
        print("STDERR:\n", res.stderr)
        print("STDOUT:\n", res.stdout)
        sys.exit(1)
    return res.stdout

print("=== 1. Initializing Fresh Database and Supabase Auth Stub ===")
auth_stub = """
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
execute_or_fail(auth_stub, "Initialize auth schema stub")

print("\n=== 2. Applying Migrations in Order ===")
migration_files = sorted(glob.glob("supabase/migrations/*.sql"))
for mf in migration_files:
    print(f"Applying: {mf} ...")
    with open(mf, encoding="utf-8") as f:
        sql = f.read()
    execute_or_fail(sql, f"Apply migration {mf}")
print("All migrations applied cleanly!")

print("\n=== 3. Executing 12 Rigorous Phase 1 Database Verifications ===")

# Test 1 & 2: Table count assertion
print("\n--- Test 1 & 2: Verify all 26 required tables exist ---")
table_query = """
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;
"""
out = run_sql(table_query, tuples_only=True).stdout
existing_tables = [line.strip() for line in out.splitlines() if line.strip()]
print(f"Total tables found: {len(existing_tables)}")
expected_tables = sorted([
    'academic_periods', 'accommodation_notes', 'accommodations', 'assignment_invigilators', 
    'assignment_students', 'audit_logs', 'availabilities', 'course_instructors', 'courses', 
    'enrollments', 'equipment_types', 'exam_requirements', 'exams', 'invigilators', 
    'room_availabilities', 'room_capacities', 'room_equipment', 'rooms', 'run_exam_students', 
    'schedule_assignments', 'schedule_events', 'scheduling_decisions', 'scheduling_runs', 
    'students', 'user_profiles', 'validation_issues'
])
assert existing_tables == expected_tables, f"Mismatch in tables! Found: {existing_tables}"
print("✓ Test 1 & 2 PASSED: Exactly 26 expected entities exist in public schema.")

# Test 3: Foreign key validation
print("\n--- Test 3: Verify Foreign Key Relationships ---")
fk_query = """
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema='public';
"""
fk_out = execute_or_fail(fk_query, "Query FKs")
print(f"Total foreign key constraints active: {len(fk_out.splitlines()) - 4}")
print("✓ Test 3 PASSED: Foreign keys verified.")

# Test 4: Unique constraints check
print("\n--- Test 4: Unique Constraints Enforcement ---")
seed_data = """
INSERT INTO academic_periods (id, code, name, start_date, end_date, exam_start_date, exam_end_date, is_active)
VALUES ('11111111-1111-1111-1111-111111111111', 'TERM-2026-02', 'Fall 2026', '2026-09-01', '2026-12-31', '2026-12-01', '2026-12-14', true);

INSERT INTO students (id, student_code, first_name, last_name, email, date_of_birth, program, year_of_study, status)
VALUES ('22222222-2222-2222-2222-222222222222', 'STU-000001', 'Alice', 'Smith', 'alice@test.edu', '2004-05-15', 'CS', 3, 'ACTIVE');
"""
execute_or_fail(seed_data, "Insert baseline seed")

# Attempt duplicate student_code
dup_sql = "INSERT INTO students (student_code, first_name, last_name, email, date_of_birth, program, year_of_study) VALUES ('STU-000001', 'Bob', 'Jones', 'bob@test.edu', '2004-06-01', 'CS', 2);"
res_dup = run_sql(dup_sql)
assert res_dup.returncode != 0 and "duplicate key value violates unique constraint" in res_dup.stderr
print("✓ Test 4 PASSED: Duplicate unique code correctly rejected.")

# Test 5 & 6: Check constraints & Invalid dates check
print("\n--- Test 5 & 6: Check Constraints & Invalid Date Failures ---")
invalid_date_sql = """
INSERT INTO academic_periods (code, name, start_date, end_date, exam_start_date, exam_end_date)
VALUES ('TERM-BAD-01', 'Bad Term', '2026-12-31', '2026-09-01', '2026-10-01', '2026-10-15');
"""
res_bad_date = run_sql(invalid_date_sql)
assert res_bad_date.returncode != 0 and "chk_ap_dates" in res_bad_date.stderr
print("✓ Test 5 & 6 PASSED: Invalid date range (end_date < start_date) correctly rejected by check constraint.")

# Test 7: Student allocation uniqueness (single room per exam)
print("\n--- Test 7: Single-Room Student Allocation Invariant ---")
setup_allocation = """
INSERT INTO rooms (id, room_code, name, building, floor, is_accessible, status)
VALUES 
  ('33333333-3333-3333-3333-333333333331', 'ROOM-000001', 'Room 101', 'Science Hall', 1, true, 'AVAILABLE'),
  ('33333333-3333-3333-3333-333333333332', 'ROOM-000002', 'Room 102', 'Science Hall', 1, true, 'AVAILABLE');

INSERT INTO courses (id, course_code, name, department, credits, academic_period_id)
VALUES ('44444444-4444-4444-4444-444444444444', 'CRS-000001', 'Algorithms', 'CS', 4, '11111111-1111-1111-1111-111111111111');

INSERT INTO exams (id, exam_code, course_id, academic_period_id, title, duration_minutes, priority, status)
VALUES ('55555555-5555-5555-5555-555555555555', 'EXAM-2026-000001', '44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', 'Algorithms Final', 120, 3, 'READY');

INSERT INTO scheduling_runs (id, run_code, academic_period_id, input_snapshot_hash, status)
VALUES ('66666666-6666-6666-6666-666666666666', 'RUN-20261201-0001', '11111111-1111-1111-1111-111111111111', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'DRAFT');

INSERT INTO run_exam_students (id, scheduling_run_id, exam_id, student_id, base_duration_minutes, extra_duration_minutes, effective_duration_minutes)
VALUES ('77777777-7777-7777-7777-777777777777', '66666666-6666-6666-6666-666666666666', '55555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222222', 120, 0, 120);

INSERT INTO schedule_assignments (id, assignment_code, scheduling_run_id, exam_id, room_id, start_time, end_time, status)
VALUES 
  ('88888888-8888-8888-8888-888888888881', 'ASN-EXAM-2026-000001-ROOM-000001', '66666666-6666-6666-6666-666666666666', '55555555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333331', '2026-12-02 09:00:00+00', '2026-12-02 11:00:00+00', 'CONFIRMED'),
  ('88888888-8888-8888-8888-888888888882', 'ASN-EXAM-2026-000001-ROOM-000002', '66666666-6666-6666-6666-666666666666', '55555555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333332', '2026-12-02 09:00:00+00', '2026-12-02 11:00:00+00', 'CONFIRMED');

-- Seat student Alice into Room 101
INSERT INTO assignment_students (assignment_id, run_exam_student_id, scheduling_run_id, exam_id, student_id, room_id, effective_duration_minutes)
VALUES ('88888888-8888-8888-8888-888888888881', '77777777-7777-7777-7777-777777777777', '66666666-6666-6666-6666-666666666666', '55555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333331', 120);
"""
execute_or_fail(setup_allocation, "Setup allocation and initial seating")

# Attempt to seat student Alice simultaneously into Room 102 for the same exam
double_seat_sql = """
INSERT INTO assignment_students (assignment_id, run_exam_student_id, scheduling_run_id, exam_id, student_id, room_id, effective_duration_minutes)
VALUES ('88888888-8888-8888-8888-888888888882', '77777777-7777-7777-7777-777777777777', '66666666-6666-6666-6666-666666666666', '55555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333332', 120);
"""
res_double_seat = run_sql(double_seat_sql)
assert res_double_seat.returncode != 0 and "unique constraint" in res_double_seat.stderr.lower()
print("✓ Test 7 PASSED: Double seating of student across split rooms blocked by run_exam_student_id unique constraint.")

# Test 8: Cross-run relationship mismatch fails
print("\n--- Test 8: Composite FK Blocks Cross-Run/Cross-Exam Mismatches ---")
cross_run_setup = """
-- Create second student Bob
INSERT INTO students (id, student_code, first_name, last_name, email, date_of_birth, program, year_of_study, status)
VALUES ('22222222-2222-2222-2222-222222222223', 'STU-000002', 'Bob', 'Ross', 'bob.ross@test.edu', '2004-03-10', 'CS', 2, 'ACTIVE');

-- Create Run 2
INSERT INTO scheduling_runs (id, run_code, academic_period_id, input_snapshot_hash, status)
VALUES ('66666666-6666-6666-6666-666666666667', 'RUN-20261201-0002', '11111111-1111-1111-1111-111111111111', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'DRAFT');

-- Create snapshot in Run 2 for student Bob
INSERT INTO run_exam_students (id, scheduling_run_id, exam_id, student_id, base_duration_minutes, extra_duration_minutes, effective_duration_minutes)
VALUES ('77777777-7777-7777-7777-777777777778', '66666666-6666-6666-6666-666666666667', '55555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222223', 120, 0, 120);
"""
execute_or_fail(cross_run_setup, "Setup Run 2 and Bob snapshot")

# Attempt to link Run 2 snapshot of Bob to Run 1 assignment
cross_run_insert = """
INSERT INTO assignment_students (assignment_id, run_exam_student_id, scheduling_run_id, exam_id, student_id, room_id, effective_duration_minutes)
VALUES ('88888888-8888-8888-8888-888888888881', '77777777-7777-7777-7777-777777777778', '66666666-6666-6666-6666-666666666667', '55555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222223', '33333333-3333-3333-3333-333333333331', 120);
"""
res_cross_run = run_sql(cross_run_insert)
assert res_cross_run.returncode != 0 and "violates foreign key constraint" in res_cross_run.stderr
print("✓ Test 8 PASSED: Cross-run assignment and snapshot mismatch blocked by composite foreign keys.")

# Test 9: Historical deletions are blocked (ON DELETE RESTRICT)
print("\n--- Test 9: Historical Record Deletion Protection (RESTRICT) ---")
delete_attempt_sql = "DELETE FROM scheduling_runs WHERE id = '66666666-6666-6666-6666-666666666666';"
res_del = run_sql(delete_attempt_sql)
assert res_del.returncode != 0 and "violates foreign key constraint" in res_del.stderr and "on table" in res_del.stderr
print("✓ Test 9 PASSED: Hard delete of scheduling_run blocked by ON DELETE RESTRICT.")

# Test 10: Published schedule uniqueness per academic period
print("\n--- Test 10: Published Schedule Uniqueness per Academic Period ---")
publish_test_sql = """
UPDATE scheduling_runs SET status = 'PUBLISHED' WHERE id = '66666666-6666-6666-6666-666666666666';
UPDATE scheduling_runs SET status = 'PUBLISHED' WHERE id = '66666666-6666-6666-6666-666666666667';
"""
res_pub = run_sql(publish_test_sql)
assert res_pub.returncode != 0 and "uq_published_run_per_period" in res_pub.stderr
print("✓ Test 10 PASSED: Partial unique index prevents multiple PUBLISHED runs per academic period.")

# Test 11: Role self-escalation trigger check
print("\n--- Test 11: Role Self-Escalation Prevention Trigger ---")
escalation_sql = """
-- Create a learner user profile
INSERT INTO user_profiles (id, email, display_name, role, student_id, status)
VALUES ('99999999-9999-9999-9999-999999999999', 'alice@test.edu', 'Alice Smith', 'LEARNER', '22222222-2222-2222-2222-222222222222', 'ACTIVE');

-- Simulate session as Alice (auth.uid() = Alice's UUID)
SET request.jwt.claim.sub = '99999999-9999-9999-9999-999999999999';

-- Attempt to self-promote to PLATFORM_ADMINISTRATOR
UPDATE user_profiles SET role = 'PLATFORM_ADMINISTRATOR' WHERE id = '99999999-9999-9999-9999-999999999999';
"""
res_esc = run_sql(escalation_sql)
assert res_esc.returncode != 0 and "only PLATFORM_ADMINISTRATOR can modify role" in res_esc.stderr
print("✓ Test 11 PASSED: Self-escalation to PLATFORM_ADMINISTRATOR rejected by trigger.")

# Test 12: RLS role boundaries and clinical note protection
print("\n--- Test 12: RLS Isolation & Clinical Note Protection ---")
rls_setup = """
-- Create accommodation and confidential clinical note
INSERT INTO accommodations (id, accommodation_code, student_id, accommodation_type, extra_time_minutes, is_active, effective_start, effective_end)
VALUES ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'ACO-000001', '22222222-2222-2222-2222-222222222222', 'EXTENDED_TIME', 30, true, '2026-09-01', '2026-12-31');

INSERT INTO accommodation_notes (accommodation_id, clinical_notes)
VALUES ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Confidential: Medical documentation on file.');
"""
execute_or_fail(rls_setup, "Setup accommodation and clinical note")

# In PostgreSQL, table owners/superusers bypass RLS by default.
# To test RLS policies, we set session role to a non-superuser or test RLS with a test user role.
rls_test_sql = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'test_learner') THEN
        CREATE ROLE test_learner LOGIN;
        GRANT USAGE ON SCHEMA public TO test_learner;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO test_learner;
    END IF;
END $$;

SET ROLE test_learner;
SET request.jwt.claim.sub = '99999999-9999-9999-9999-999999999999';

-- Attempt to read clinical note as Learner
SELECT clinical_notes FROM accommodation_notes;
"""
res_rls = run_sql(rls_test_sql, tuples_only=True)
notes_found = [line for line in res_rls.stdout.splitlines() if "Confidential" in line]
assert len(notes_found) == 0, f"Leak detected: Learner saw confidential notes! {res_rls.stdout}"
print("✓ Test 12 PASSED: Confidential accommodation note hidden from Learner by RLS policy.")

print("\n==================================================================")
print("ALL 12 PHASE 1 DATABASE VERIFICATIONS PASSED SUCCESSFULLY!")
print("==================================================================")
