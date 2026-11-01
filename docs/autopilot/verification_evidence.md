# ExamOps Autopilot — Verification Evidence

> **Document**: Autopilot Empirical Verification Evidence  
> **System**: ExamOps Autonomous Engineering Engine  
> **Last Updated**: 2026-11-01T18:03:00+05:30  

---

## Verification Evidence Log

### Phase 0 Verifications

#### Tooling Verification
- `python --version` $\to$ `Python 3.12.10`
- `node --version` $\to$ `v24.22.1`
- `npm.cmd --version` $\to$ `11.19.1`
- `npx.cmd supabase --version` $\to$ `2.122.0`
- `docker --version` $\to$ `Docker version 29.9.2, build a82e528`
- `git --version` $\to$ `git version 2.56.0.windows.3`

#### Pass A: Design & Implementation Audit
- **Reviewer Perspective**: Senior Staff Engineer
- **Audit Findings**:
  - Entity topological dependencies reconciled: `user_profiles` created before `course_instructors` and `scheduling_runs`.
  - Snapshot & seating relational integrity reinforced with composite foreign keys `(assignment_id, scheduling_run_id, exam_id, room_id)` and `(run_exam_student_id, scheduling_run_id, exam_id, student_id)`.
  - Non-recursive RLS policy design implemented via `SECURITY DEFINER` functions (`get_auth_role()`, `get_auth_student_id()`, `get_auth_invigilator_id()`).
  - Pessimistic publication row locking (`SELECT id FROM academic_periods WHERE id = period_id FOR UPDATE`) incorporated into concurrency architecture.
  - Terminology verified: zero references to "Proctor" remain in active design contracts.

#### Pass B: Execution & Evidence Audit
- **Reviewer Perspective**: Independent QA Engineer
- **Command Executed**: `python scripts/verify_phase0.py`
  - **Output**:
    ```
    Data Dictionary tables (26):
      ['academic_periods', 'accommodation_notes', 'accommodations', 'assignment_invigilators', 'assignment_students', 'audit_logs', 'availabilities', 'course_instructors', 'courses', 'enrollments', 'equipment_types', 'exam_requirements', 'exams', 'invigilators', 'room_availabilities', 'room_capacities', 'room_equipment', 'rooms', 'run_exam_students', 'schedule_assignments', 'schedule_events', 'scheduling_decisions', 'scheduling_runs', 'students', 'user_profiles', 'validation_issues']

    Permissions tables (26):
      ['academic_periods', 'accommodation_notes', 'accommodations', 'assignment_invigilators', 'assignment_students', 'audit_logs', 'availabilities', 'course_instructors', 'courses', 'enrollments', 'equipment_types', 'exam_requirements', 'exams', 'invigilators', 'room_availabilities', 'room_capacities', 'room_equipment', 'rooms', 'run_exam_students', 'schedule_assignments', 'schedule_events', 'scheduling_decisions', 'scheduling_runs', 'students', 'user_profiles', 'validation_issues']

    ERD Entity Blocks (26):
      ['AcademicPeriod', 'Accommodation', 'AccommodationNote', 'AssignmentInvigilator', 'AssignmentStudent', 'AuditLog', 'Availability', 'Course', 'CourseInstructor', 'Enrollment', 'EquipmentType', 'Exam', 'ExamRequirement', 'Invigilator', 'Room', 'RoomAvailability', 'RoomCapacity', 'RoomEquipment', 'RunExamStudent', 'ScheduleAssignment', 'ScheduleEvent', 'SchedulingDecision', 'SchedulingRun', 'Student', 'UserProfile', 'ValidationIssue']

    SUCCESS: All 26 entities are identical and fully reconciled across ERD, Data Dictionary, and Permissions Matrix!
    ```
- **Terminology Verification**: Case-insensitive regex scan across all markdown files in `docs/` returned `ZERO proctor references found in active docs!`.
- **Exit Gate Status**: PASSED.

---

### Phase 1 Verifications: Database Implementation

#### Pass A: Design & Implementation Audit
- **Reviewer Perspective**: Senior Database Architect / Principal Engineer
- **Audit Findings**:
  - Full relational normalization across all 26 entities.
  - Zero circular migration dependencies; `user_profiles` created in `001_core_master_and_security.sql` prior to referencing tables.
  - Bulletproof composite integrity constraints `fk_asgn_sa_composite` and `fk_asgn_res_composite` enforced on `assignment_students`.
  - Non-recursive RLS architecture with `SECURITY DEFINER` helper functions (`get_auth_role()`, `get_auth_student_id()`, `get_auth_invigilator_id()`).
  - Immutable trigger `trg_user_profile_immutability` defends role and identity foreign keys.
  - Append-only immutability triggers `trg_audit_logs_immutable`, `trg_decisions_immutable`, `trg_events_immutable`.
  - Atomic publication procedure `publish_schedule_run` implements pessimistic row locking (`FOR UPDATE`) on `academic_periods`.

#### Pass B: Execution & Evidence Audit
- **Reviewer Perspective**: Independent QA Engineer
- **Environment**: Real PostgreSQL 16 instance (`PostgreSQL 16.15 on x86_64-pc-linux-musl`, Docker container `examops-db-test`).
- **Command Executed**: `python scripts/apply_and_test_database.py`
  - **Output**:
    ```
    === 1. Initializing Fresh Database and Supabase Auth Stub ===
    === 2. Applying Migrations in Order ===
    Applying: supabase/migrations\001_core_master_and_security.sql ...
    Applying: supabase/migrations\002_scheduling_engine.sql ...
    Applying: supabase/migrations\003_rls_and_policies.sql ...
    All migrations applied cleanly!

    === 3. Executing 12 Rigorous Phase 1 Database Verifications ===
    --- Test 1 & 2: Verify all 26 required tables exist ---
    Total tables found: 26
    ✓ Test 1 & 2 PASSED: Exactly 26 expected entities exist in public schema.
    --- Test 3: Verify Foreign Key Relationships ---
    Total foreign key constraints active: 75
    ✓ Test 3 PASSED: Foreign keys verified.
    --- Test 4: Unique Constraints Enforcement ---
    ✓ Test 4 PASSED: Duplicate unique code correctly rejected.
    --- Test 5 & 6: Check Constraints & Invalid Date Failures ---
    ✓ Test 5 & 6 PASSED: Invalid date range (end_date < start_date) correctly rejected by check constraint.
    --- Test 7: Single-Room Student Allocation Invariant ---
    ✓ Test 7 PASSED: Double seating of student across split rooms blocked by run_exam_student_id unique constraint.
    --- Test 8: Composite FK Blocks Cross-Run/Cross-Exam Mismatches ---
    ✓ Test 8 PASSED: Cross-run assignment and snapshot mismatch blocked by composite foreign keys.
    --- Test 9: Historical Record Deletion Protection (RESTRICT) ---
    ✓ Test 9 PASSED: Hard delete of scheduling_run blocked by ON DELETE RESTRICT.
    --- Test 10: Published Schedule Uniqueness per Academic Period ---
    ✓ Test 10 PASSED: Partial unique index prevents multiple PUBLISHED runs per academic period.
    --- Test 11: Role Self-Escalation Prevention Trigger ---
    ✓ Test 11 PASSED: Self-escalation to PLATFORM_ADMINISTRATOR rejected by trigger.
    --- Test 12: RLS Isolation & Clinical Note Protection ---
    ✓ Test 12 PASSED: Confidential accommodation note hidden from Learner by RLS policy.
    ==================================================================
    ALL 12 PHASE 1 DATABASE VERIFICATIONS PASSED SUCCESSFULLY!
    ==================================================================
    ```
- **Exit Gate Status**: PASSED.
