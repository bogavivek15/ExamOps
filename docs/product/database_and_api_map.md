# ExamOps — Database Schema & Backend API Map

> **Database Engine**: Supabase Cloud PostgreSQL 17.11  
> **Backend Framework**: Python 3.12 + FastAPI + Pydantic v2  
> **Schema Tables**: 26 Normalized Relational Tables with Composite Integrity & Non-Repudiation Triggers  
> **Security Model**: Row Level Security (RLS) + FastAPI RBAC Dependencies

---

## 1. Database Entity-Relationship Architecture

The database comprises 26 tables categorized into 4 operational layers:

```
+─────────────────────────────────────────────────────────────────────────────+
|                         EXAMOPS DATABASE SCHEMATIC                          |
+─────────────────────────────────────────────────────────────────────────────+
|                                                                             |
|  1. MASTER ACADEMIC LAYER                                                   |
|     academic_periods ──┬──► courses ──┬──► enrollments ◄── students         |
|                        │              │                                     |
|                        └──► exams ────┴──► exam_requirements                |
|                                                                             |
|  2. PHYSICAL & HUMAN RESOURCES LAYER                                        |
|     rooms ──┬──► room_capacities        invigilators ──► availabilities     |
|             ├──► room_availabilities                                        |
|             └──► room_equipment ◄── equipment_types                         |
|                                                                             |
|  3. ACCESSIBILITY & CLINICAL LAYER                                          |
|     students ──► accommodations ──► accommodation_notes (FERPA Encrypted)   |
|                                                                             |
|  4. SCHEDULING & GOVERNANCE LAYER                                           |
|     scheduling_runs ──┬──► run_exam_students (Frozen Input Snapshot)        |
|                       ├──► schedule_assignments ──┬──► assignment_students  |
|                       │                           └──► assignment_invigilators
|                       ├──► scheduling_decisions (Algorithmic Telemetry)     |
|                       ├──► schedule_events (State Transitions)             |
|                       ├──► validation_issues (Diagnostic Exceptions)        |
|                       └──► audit_logs (Append-Only Immutable Ledger)        |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Complete 26 Tables Catalog

| # | Table Name | Purpose | Key Primary & Foreign Keys | Immutability / Triggers |
|---|---|---|---|---|
| 1 | `academic_periods` | Semester operational dates & exam window | `id` (PK, UUID), `code` (Unique) | Check constraints on date order |
| 2 | `students` | Student registry master | `id` (PK, UUID), `student_code` (Unique) | Check regex on `STU-[0-9]{6}` |
| 3 | `courses` | Course catalog | `id` (PK, UUID), `course_code` (Unique) | FK to `academic_periods` |
| 4 | `course_instructors` | Faculty teaching assignments | `(course_id, instructor_id)` (Composite PK) | FKs to `courses`, `user_profiles` |
| 5 | `enrollments` | Student course registrations | `(student_id, course_id, academic_period_id)` (Unique) | FKs to `students`, `courses`, `academic_periods` |
| 6 | `exams` | Final examination definitions | `id` (PK, UUID), `exam_code` (Unique) | Check regex on `EXAM-[0-9]{4}-[0-9]{6}` |
| 7 | `exam_requirements` | Technical & physical exam requirements | `id` (PK, UUID), `exam_id` (FK) | Unique `(exam_id, requirement_type)` |
| 8 | `rooms` | Campus examination venues | `id` (PK, UUID), `room_code` (Unique) | Check regex on `ROOM-[0-9]{6}` |
| 9 | `room_capacities` | Effective examination desk counts | `id` (PK, UUID), `room_id` (FK) | Effective dating support |
| 10 | `equipment_types` | Physical equipment taxonomy | `id` (PK, UUID), `code` (Unique) | AV, Computing, Lab, Accessibility |
| 11 | `room_equipment` | Hardware installed in rooms | `(room_id, equipment_type_id)` (Composite PK) | FKs to `rooms`, `equipment_types` |
| 12 | `room_availabilities` | Room operating windows & closures | `id` (PK, UUID), `room_id` (FK) | Check start/end time validity |
| 13 | `invigilators` | Proctor staff directory | `id` (PK, UUID), `invigilator_code` (Unique) | Check regex on `INV-[0-9]{6}` |
| 14 | `availabilities` | Individual proctor working periods | `id` (PK, UUID), `invigilator_id` (FK) | Day of week & time boundaries |
| 15 | `accommodations` | Accessibility adjustments | `id` (PK, UUID), `student_id` (FK) | Extra minutes, room feature flags |
| 16 | `accommodation_notes` | Sensitive clinical documentation | `id` (PK, UUID), `accommodation_id` (FK) | FERPA Protected / Redacted in API |
| 17 | `user_profiles` | Application operator accounts & roles | `id` (PK, UUID), `email` (Unique) | Role immutability trigger |
| 18 | `scheduling_runs` | Timetable generation runs | `id` (PK, UUID), `run_code` (Unique) | Partial unique index on PUBLISHED |
| 19 | `schedule_assignments` | Confirmed room-exam timeslot blocks | `(id, scheduling_run_id, exam_id, room_id)` (Unique) | Assignment code `ASN-...` |
| 20 | `run_exam_students` | Frozen participant snapshot | `(scheduling_run_id, exam_id, student_id)` (Unique) | Immutable run input boundary |
| 21 | `assignment_students` | Individual desk seat allocations | `(assignment_id, student_id)` (Unique) | Composite FKs to `sa` and `res` |
| 22 | `assignment_invigilators` | Proctor room supervision shifts | `(assignment_id, invigilator_id)` (Unique) | PRIMARY / SECONDARY role |
| 23 | `scheduling_decisions` | Algorithmic telemetry & reasons | `(scheduling_run_id, exam_id)` (Unique) | Immutable ledger trigger |
| 24 | `schedule_events` | State transition audit log | `id` (PK, UUID), `scheduling_run_id` (FK) | Immutable trigger |
| 25 | `validation_issues` | Diagnostic hard-constraint exceptions | `id` (PK, UUID), `scheduling_run_id` (FK) | CRITICAL / WARNING severity |
| 26 | `audit_logs` | Non-repudiable audit ledger | `id` (PK, UUID), `created_at` (TIMESTAMPTZ) | Append-only trigger (`trg_audit_immutable`) |

---

## 3. Database Security, Immutability & Stored Procedures

### Append-Only Immutability Triggers
The following database trigger is active on `audit_logs`, `scheduling_decisions`, and `schedule_events`:
```sql
CREATE OR REPLACE FUNCTION public.prevent_modification_of_immutable_logs()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Disallowed: table % is append-only and cannot be updated or deleted.', TG_TABLE_NAME;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```
Any attempt to execute an SQL `UPDATE` or `DELETE` on these tables throws PostgreSQL exception `P0001`.

### Atomic Publication Stored Procedure (`publish_schedule_run`)
To guarantee that exactly one published schedule exists per academic period without race conditions:
```sql
CREATE OR REPLACE FUNCTION public.publish_schedule_run(
    p_run_id UUID,
    p_operator_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_period_id UUID;
BEGIN
    -- Acquire exclusive row lock on the target run
    SELECT academic_period_id INTO v_period_id
    FROM scheduling_runs
    WHERE id = p_run_id
    FOR UPDATE;

    -- Supersede any previously published run for this academic period
    UPDATE scheduling_runs
    SET status = 'SUPERSEDED', updated_at = NOW()
    WHERE academic_period_id = v_period_id AND status = 'PUBLISHED' AND id != p_run_id;

    -- Atomically promote target run to PUBLISHED
    UPDATE scheduling_runs
    SET status = 'PUBLISHED', updated_at = NOW()
    WHERE id = p_run_id;

    RETURN jsonb_build_object('success', true, 'status', 'PUBLISHED');
END;
$$;
```

---

## 4. Complete Backend API Route Map

All endpoints are hosted under `http://127.0.0.1:8000/api` and documented in OpenAPI Swagger (`/docs`).

### Authentication & Profiles (`/api/auth`)
| Method | Path | Allowed Roles | Description |
|---|---|---|---|
| `POST` | `/auth/login` | Public | Authenticates user credentials, returns signed Bearer JWT and user profile. |
| `GET` | `/auth/me` | Authenticated | Resolves currently authenticated user from Bearer JWT. |
| `GET` | `/auth/profiles` | Admins (`ACADEMIC_ADMINISTRATOR`, `PLATFORM_ADMINISTRATOR`) | Lists all operator user profiles and assigned roles. |
| `POST` | `/auth/dev-switch-role` | Development Only | Switches simulated role context. Blocked with HTTP 403 in `production`. |

### Scheduling Operations (`/api/scheduling`)
| Method | Path | Allowed Roles | Description |
|---|---|---|---|
| `GET` | `/scheduling/runs` | All Authenticated | Lists all historical scheduling runs with completion metrics. |
| `POST` | `/scheduling/runs` | Admins, Exam Officers | Creates a new scheduling run in `DRAFT` status with frozen input snapshot. |
| `GET` | `/scheduling/runs/{id}` | All Authenticated | Retrieves detailed run metadata and status. |
| `POST` | `/scheduling/runs/{id}/execute` | Admins, Exam Officers | Executes deterministic heuristic scheduling engine against live dataset. |
| `GET` | `/scheduling/runs/{id}/assignments` | All Authenticated | Retrieves paginated list of confirmed room assignments. |
| `GET` | `/scheduling/runs/{id}/decisions` | All Authenticated | Retrieves algorithmic telemetry, evaluated candidate slots, and reason codes. |
| `GET` | `/scheduling/runs/{id}/issues` | All Authenticated | Retrieves independent validation issues for the run. |
| `GET` | `/scheduling/runs/{id}/reconciliation` | All Authenticated | Retrieves resource usage reconciliation calculations. |
| `POST` | `/scheduling/runs/{id}/approve` | Admins, Exam Officers | Advances run status to `APPROVED`. |
| `POST` | `/scheduling/runs/{id}/publish` | Admins, Exam Officers | Publishes run via PostgreSQL row-locked stored procedure. |

### Academic Masters (`/api/exams`, `/api/students`, `/api/courses`)
| Method | Path | Allowed Roles | Description |
|---|---|---|---|
| `GET` | `/exams` | All Authenticated | Paginated examination directory with keyword search and status filter. |
| `GET` | `/exams/{id}` | All Authenticated | Detailed examination profile. |
| `GET` | `/exams/{id}/requirements` | All Authenticated | Required equipment, lab facilities, and duration. |
| `GET` | `/students` | All Authenticated | Paginated student registry with search and department filters. |
| `GET` | `/students/{id}` | All Authenticated | Student profile and program level. |
| `GET` | `/students/{id}/schedule` | All Authenticated | Individual student examination timetable and assigned desks. |
| `GET` | `/courses` | All Authenticated | Course catalog with enrolled student counts. |
| `GET` | `/courses/{id}` | All Authenticated | Course profile and syllabus info. |
| `GET` | `/enrollments` | All Authenticated | Active course enrollment rosters. |

### Physical & Human Resources (`/api/rooms`, `/api/invigilators`)
| Method | Path | Allowed Roles | Description |
|---|---|---|---|
| `GET` | `/rooms` | All Authenticated | Paginated examination venues with accessibility filter. |
| `GET` | `/rooms/{id}` | All Authenticated | Room profile, installed equipment, and operating hours. |
| `GET` | `/invigilators` | All Authenticated | Proctor staff directory with workload caps. |
| `GET` | `/invigilators/{id}` | All Authenticated | Proctor profile. |
| `GET` | `/invigilators/{id}/schedule` | All Authenticated | Assigned proctoring shifts and room locations. |

### Accessibility & Confidential Notes (`/api/accommodations`)
| Method | Path | Allowed Roles | Description |
|---|---|---|---|
| `GET` | `/accommodations` | All Authenticated | List of active accommodations (extra time, room features). |
| `GET` | `/accommodations/{id}/notes` | Role-Masked | Full decrypted clinical notes for Admins; `[REDACTED]` for Learners. |

### Analytics, Exports & Governance (`/api/analytics`, `/api/export`, `/api/audit`)
| Method | Path | Allowed Roles | Description |
|---|---|---|---|
| `GET` | `/analytics/overview` | All Authenticated | High-level KPI metrics, active period banner, and run summary. |
| `GET` | `/export/runs/{id}/csv` | All Authenticated | Downloads master examination timetable in standard CSV format. |
| `GET` | `/export/runs/{id}/json` | All Authenticated | Downloads structured master timetable in machine-readable JSON. |
| `GET` | `/audit/logs` | Admins (`ACADEMIC_ADMINISTRATOR`, `PLATFORM_ADMINISTRATOR`) | Chronological audit ledger with actor emails and actions. |
| `GET` | `/audit/events` | Admins (`ACADEMIC_ADMINISTRATOR`, `PLATFORM_ADMINISTRATOR`) | State transition before-and-after JSON snapshots. |

