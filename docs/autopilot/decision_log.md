# ExamOps Autopilot — Decision Log

> **Document**: Autopilot Architectural and Engineering Decisions  
> **System**: ExamOps Autonomous Engineering Engine  
> **Last Updated**: 2026-11-01T17:58:00+05:30  

---

## Architectural Decisions

### `DEC-001`: Topological Schema Migration Order
- **Context**: `user_profiles` is referenced by `course_instructors` (`instructor_profile_id`), `accommodation_notes` (`approved_by`), `scheduling_runs` (`created_by`), `validation_issues` (`resolved_by`), and `audit_logs` (`user_id`).
- **Decision**: Define and create `user_profiles` in the foundational core migration alongside reference master data (`academic_periods`, `students`, `invigilators`), before `courses` and downstream operational tables.
- **Consequence**: Zero forward foreign key references or alter table patching needed during migration replay.

### `DEC-002`: Composite Integrity for Student Room Allocation
- **Context**: Students are snapshotted in `run_exam_students` and assigned to rooms in `assignment_students`. Simple foreign keys could allow assigning a snapshot from Run A into a room assignment belonging to Run B.
- **Decision**: Include `(scheduling_run_id, exam_id)` in `assignment_students` and enforce composite foreign keys to both `schedule_assignments(id, scheduling_run_id, exam_id, room_id)` and `run_exam_students(id, scheduling_run_id, exam_id, student_id)`.
- **Consequence**: PostgreSQL database engine guarantees that cross-run and cross-exam allocations are structurally impossible.

### `DEC-003`: Non-Recursive RLS Functions for User Profiles
- **Context**: Evaluating `user_profiles` RLS using subqueries on `user_profiles` causes infinite recursion errors in PostgreSQL.
- **Decision**: Create `SECURITY DEFINER` helper functions (`get_auth_role()`, `get_auth_student_id()`, `get_auth_invigilator_id()`) with strict `search_path = public` to read current user role and linkage without re-triggering RLS. Enforce role column immutability with a `BEFORE UPDATE` trigger.
- **Consequence**: Fast, non-recursive RLS policy checks and ironclad role self-escalation protection.

### `DEC-004`: Serialized Schedule Publication with Academic Period Row Locking
- **Context**: Concurrent publication requests could attempt to publish conflicting schedules simultaneously.
- **Decision**: Publications acquire an exclusive row lock on `academic_periods` (`SELECT ... FOR UPDATE`), check existing published runs, atomically update previous published runs to `SUPERSEDED`, and set target run to `PUBLISHED`, backed by a partial unique index `(academic_period_id) WHERE (status = 'PUBLISHED')`.
- **Consequence**: Guaranteed linearizable schedule publication with zero race conditions.

### `DEC-005`: Role Aliasing in Dependency-Injected Authentication
- **Context**: Frontend client conventions and problem documentation refer to user roles as `STUDENT`, `EXAM_OFFICER`, and `SUPER_ADMIN`, whereas the PostgreSQL database enum constraint uses `LEARNER`, `ACADEMIC_ADMINISTRATOR`, and `PLATFORM_ADMINISTRATOR`.
- **Decision**: Maintain a bidirectional `ROLE_ALIASES` mapping in `backend/auth.py`. Route handlers and dependency checkers accept both external and database-canonical forms transparently.
- **Consequence**: Full backward and forward compatibility between API consumers, UI forms, and PostgreSQL RLS constraints.

### `DEC-006`: Chunked Bulk Insert Optimization for High-Volume Seatings
- **Context**: Persisting an institutional schedule run produces 25,000+ student room seatings and hundreds of invigilator staffings. Executing individual `INSERT` queries took 35-40 seconds.
- **Decision**: Implement `psycopg2.extras.execute_values` with chunk sizes of 1,000 to 2,000 rows across `run_exam_students`, `schedule_assignments`, `assignment_students`, and `scheduling_decisions`.
- **Consequence**: Full run persistence latency reduced from ~40s to <1.0s while preserving all composite foreign key guarantees.
