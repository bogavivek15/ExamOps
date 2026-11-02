# ExamOps Comprehensive Database Inventory & Schema Catalog

**Audit Date**: 2026-11-02  
**Target Environment**: Supabase Managed PostgreSQL 17.11 (aarch64)  
**Project Reference**: `ndlysanfeowexvtlvhxd`  
**Connection Endpoint**: `aws-1-eu-west-3.pooler.supabase.com:5432/postgres` (SSL Enabled, Transaction Pooling)  
**Schema**: `public`  
**Total Entities**: 26 of 26 Core & Supporting Entities Verified  
**Total Records Audited**: 758,588 Rows  

---

## 1. Executive Summary & Inventory Overview

The ExamOps PostgreSQL database schema comprises 26 relation tables organized into Master Reference, Operational Facilities, Enrollment & Participation, Scheduling Engine, Governance & Audit domains. All 26 tables have Row-Level Security (RLS) enabled, strict primary key definitions (UUID v4 default `gen_random_uuid()`), and explicit foreign keys with referential integrity rules (`ON DELETE RESTRICT` or `ON DELETE CASCADE`).

| Table Name | Category | Primary Key | Exact Row Count | RLS Enabled | Triggers |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `academic_periods` | Master Reference | `id` (UUID) | 1 | Yes | - |
| `students` | Master Reference | `id` (UUID) | 5,000 | Yes | - |
| `courses` | Master Reference | `id` (UUID) | 150 | Yes | - |
| `course_instructors` | Master Reference | `id` (UUID) | 150 | Yes | - |
| `enrollments` | Master Operational | `id` (UUID) | 25,044 | Yes | - |
| `exams` | Master Operational | `id` (UUID) | 300 | Yes | - |
| `exam_requirements` | Master Operational | `id` (UUID) | 107 | Yes | - |
| `rooms` | Facilities Master | `id` (UUID) | 100 | Yes | - |
| `room_capacities` | Facilities Operational | `id` (UUID) | 100 | Yes | - |
| `equipment_types` | Catalog | `id` (UUID) | 5 | Yes | - |
| `room_equipment` | Facilities Operational | `id` (UUID) | 136 | Yes | - |
| `room_availabilities` | Facilities Operational | `id` (UUID) | 601 | Yes | - |
| `invigilators` | Faculty/Staff Master | `id` (UUID) | 200 | Yes | - |
| `availabilities` | Faculty/Staff Operational | `id` (UUID) | 1,200 | Yes | - |
| `accommodations` | Student Services | `id` (UUID) | 301 | Yes | - |
| `accommodation_notes`| Confidential Medical | `id` (UUID) | 301 | Yes | - |
| `user_profiles` | Security & Auth | `id` (UUID) | 45 | Yes | `trg_user_profile_immutability` |
| `scheduling_runs` | Engine Operational | `id` (UUID) | 11 | Yes | - |
| `run_exam_students` | Engine Snapshot | `id` (UUID) | 550,968 | Yes | - |
| `schedule_assignments`| Engine Results | `id` (UUID) | 3,487 | Yes | - |
| `assignment_students` | Engine Results Bridge | `id` (UUID) | 159,555 | Yes | - |
| `assignment_invigilators`| Engine Results Bridge | `id` (UUID) | 7,568 | Yes | - |
| `scheduling_decisions`| Algorithmic Telemetry | `id` (UUID) | 3,300 | Yes | `trg_decisions_immutable` |
| `schedule_events` | State Transition Trail | `id` (UUID) | 17 | Yes | `trg_events_immutable` |
| `validation_issues` | Diagnostic Exceptions | `id` (UUID) | 0 | Yes | - |
| `audit_logs` | Append-Only Audit Trail | `id` (UUID) | 41 | Yes | `trg_audit_logs_immutable` |
| **TOTAL** | **26 Tables** | - | **758,588** | **26 / 26** | **4 Immutability Triggers** |

---

## 2. Table-by-Table Architectural Catalog

### 2.1 `academic_periods`
- **Purpose**: Defines institutional terms, active semester boundaries, and strict examination calendar windows.
- **Columns**:
  - `id` (`UUID`, PK, `gen_random_uuid()`)
  - `code` (`VARCHAR(32)`, NOT NULL, UNIQUE) — e.g., `FA-2026`
  - `name` (`VARCHAR(150)`, NOT NULL)
  - `start_date` (`DATE`, NOT NULL)
  - `end_date` (`DATE`, NOT NULL)
  - `exam_start_date` (`DATE`, NOT NULL)
  - `exam_end_date` (`DATE`, NOT NULL)
  - `is_active` (`BOOLEAN`, NOT NULL, DEFAULT `FALSE`)
  - `created_at` (`TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`)
- **Constraints**:
  - `chk_ap_dates`: `end_date >= start_date`
  - `chk_ap_exam_dates`: `exam_end_date >= exam_start_date AND exam_start_date >= start_date AND exam_end_date <= end_date`
- **Indexes**: `idx_ap_code` (BTREE on `code`), `idx_ap_is_active` (BTREE on `is_active`).

### 2.2 `students`
- **Purpose**: Master student directory with institutional codes and degree programs.
- **Columns**:
  - `id` (`UUID`, PK, `gen_random_uuid()`)
  - `student_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `STU-XXXXXX`)
  - `first_name` (`VARCHAR(100)`, NOT NULL)
  - `last_name` (`VARCHAR(100)`, NOT NULL)
  - `email` (`VARCHAR(255)`, NOT NULL, UNIQUE)
  - `date_of_birth` (`DATE`, NOT NULL)
  - `program` (`VARCHAR(150)`, NOT NULL)
  - `year_of_study` (`INTEGER`, NOT NULL, CHECK `1..6`)
  - `status` (`VARCHAR(20)`, NOT NULL, DEFAULT `'ACTIVE'`, CHECK in `('ACTIVE', 'INACTIVE', 'GRADUATED', 'SUSPENDED')`)
  - `created_at`, `updated_at` (`TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`)
- **Constraints**:
  - `chk_student_code_format`: `student_code ~ '^STU-[0-9]{6}$'`

### 2.3 `courses`
- **Purpose**: Academic course offerings mapped to academic terms.
- **Columns**:
  - `id` (`UUID`, PK)
  - `course_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `CRS-XXXXXX`)
  - `name` (`VARCHAR(200)`, NOT NULL)
  - `department` (`VARCHAR(100)`, NOT NULL)
  - `credits` (`INTEGER`, NOT NULL, CHECK `1..12`)
  - `academic_period_id` (`UUID`, NOT NULL, FK $\to$ `academic_periods(id)`)
  - `status` (`VARCHAR(20)`, NOT NULL, DEFAULT `'ACTIVE'`)
- **Constraints**: `chk_course_code_format`, `uq_course_period` (`id, academic_period_id`).

### 2.4 `enrollments`
- **Purpose**: Many-to-many relationship connecting students to courses per academic term.
- **Columns**:
  - `id` (`UUID`, PK)
  - `enrollment_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `ENR-XXXXXX`)
  - `student_id` (`UUID`, NOT NULL, FK $\to$ `students(id)`)
  - `course_id` (`UUID`, NOT NULL, FK $\to$ `courses(id)`)
  - `academic_period_id` (`UUID`, NOT NULL, FK $\to$ `academic_periods(id)`)
  - `status` (`VARCHAR(20)`, NOT NULL, DEFAULT `'ACTIVE'`)
- **Constraints**: `uq_enr_student_course` (`student_id, course_id, academic_period_id`).

### 2.5 `exams`
- **Purpose**: Formal examination entities requiring room and invigilator scheduling.
- **Columns**:
  - `id` (`UUID`, PK)
  - `exam_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `EXAM-YYYY-XXXXXX`)
  - `course_id` (`UUID`, NOT NULL, FK $\to$ `courses(id)`)
  - `academic_period_id` (`UUID`, NOT NULL, FK $\to$ `academic_periods(id)`)
  - `title` (`VARCHAR(200)`, NOT NULL)
  - `exam_type` (`VARCHAR(20)`, NOT NULL, DEFAULT `'FINAL'`, CHECK in `('FINAL', 'MIDTERM', 'SUPPLEMENTARY')`)
  - `duration_minutes` (`INTEGER`, NOT NULL, CHECK `duration_minutes > 0 AND duration_minutes <= 480`)
  - `priority` (`INTEGER`, NOT NULL, DEFAULT 3, CHECK `1..5`)
  - `status` (`VARCHAR(20)`, NOT NULL, DEFAULT `'READY'`)

### 2.6 `exam_requirements`
- **Purpose**: Specialized technical, capacity, or accessibility needs for examinations.
- **Columns**:
  - `id` (`UUID`, PK)
  - `requirement_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `REQ-XXXXXX`)
  - `exam_id` (`UUID`, NOT NULL, FK $\to$ `exams(id)` ON DELETE CASCADE)
  - `requirement_type` (`VARCHAR(50)`, NOT NULL, CHECK in `('REQUIRED_EQUIPMENT', 'ROOM_FEATURE', 'ROOM_CAPACITY_MIN')`)
  - `value` (`TEXT`, NOT NULL)
  - `unit` (`VARCHAR(20)`)
  - `is_mandatory` (`BOOLEAN`, NOT NULL, DEFAULT `TRUE`)

### 2.7 `rooms` & `room_capacities`
- **Purpose**: Physical examination facilities and time-bounded capacity configurations.
- **Columns (`rooms`)**:
  - `id` (`UUID`, PK)
  - `room_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `ROOM-XXXXXX`)
  - `name` (`VARCHAR(100)`, NOT NULL), `building` (`VARCHAR(100)`, NOT NULL), `floor` (`INTEGER`, NOT NULL)
  - `is_accessible` (`BOOLEAN`, NOT NULL, DEFAULT `FALSE`)
  - `status` (`VARCHAR(20)`, NOT NULL, DEFAULT `'AVAILABLE'`)
- **Columns (`room_capacities`)**:
  - `id` (`UUID`, PK), `capacity_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `CAP-XXXXXX`)
  - `room_id` (`UUID`, NOT NULL, FK $\to$ `rooms(id)`)
  - `standard_capacity` (`INTEGER`, NOT NULL, CHECK `> 0`)
  - `exam_capacity` (`INTEGER`, NOT NULL, CHECK `> 0 AND <= standard_capacity`)
  - `effective_start`, `effective_end` (`DATE`, NOT NULL, CHECK `effective_end >= effective_start`)

### 2.8 `invigilators` & `availabilities`
- **Purpose**: Proctors, faculty supervisors, and explicit working availability intervals.
- **Columns (`invigilators`)**:
  - `id` (`UUID`, PK), `invigilator_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `INV-XXXXXX`)
  - `first_name`, `last_name`, `email` (`VARCHAR`, NOT NULL, UNIQUE), `department` (`VARCHAR`, NOT NULL)
  - `max_hours_per_day` (`NUMERIC(4,2)`, NOT NULL, DEFAULT `8.00`, CHECK `> 0 AND <= 24.00`)
  - `max_hours_per_week` (`NUMERIC(4,2)`, NOT NULL, DEFAULT `25.00`, CHECK `> 0 AND <= 168.00`)
  - `status` (`VARCHAR(20)`, NOT NULL, DEFAULT `'ACTIVE'`)
- **Columns (`availabilities`)**:
  - `id` (`UUID`, PK), `availability_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `AVL-XXXXXX`)
  - `invigilator_id` (`UUID`, NOT NULL, FK $\to$ `invigilators(id)`)
  - `day_of_week` (`INTEGER`, CHECK `0..6`), `specific_date` (`DATE`)
  - `start_time` (`TIME`, NOT NULL), `end_time` (`TIME`, NOT NULL, CHECK `end_time > start_time`)
  - `availability_type` (`VARCHAR(20)`, NOT NULL, DEFAULT `'AVAILABLE'`, CHECK in `('AVAILABLE', 'UNAVAILABLE')`)

### 2.9 `accommodations` & `accommodation_notes`
- **Purpose**: Student disability and special needs registry, with clinical privacy isolation.
- **Columns (`accommodations`)**:
  - `id` (`UUID`, PK), `accommodation_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `ACO-XXXXXX`)
  - `student_id` (`UUID`, NOT NULL, FK $\to$ `students(id)`)
  - `accommodation_type` (`VARCHAR(50)`, NOT NULL, CHECK in `('EXTENDED_TIME', 'ACCESSIBLE_ROOM', 'LOW_DISTRACTION', 'SPECIAL_EQUIPMENT')`)
  - `extra_time_minutes` (`INTEGER`), `extra_time_percentage` (`NUMERIC(5,2)`)
  - `required_room_feature` (`TEXT`), `required_equipment` (`TEXT`)
  - `is_active` (`BOOLEAN`, NOT NULL, DEFAULT `TRUE`)
  - `effective_start`, `effective_end` (`DATE`, NOT NULL, CHECK `effective_end >= effective_start`)
- **Columns (`accommodation_notes`)**:
  - `id` (`UUID`, PK), `accommodation_id` (`UUID`, NOT NULL, UNIQUE, FK $\to$ `accommodations(id)` ON DELETE CASCADE)
  - `clinical_notes` (`TEXT`, NOT NULL)
  - `approved_by` (`UUID`, FK $\to$ `user_profiles(id)`)

### 2.10 `scheduling_runs`
- **Purpose**: Operational run instances executing the deterministic scheduling algorithm.
- **Columns**:
  - `id` (`UUID`, PK), `run_code` (`VARCHAR(32)`, NOT NULL, UNIQUE, Format: `RUN-YYYYMMDD-XXXX`)
  - `academic_period_id` (`UUID`, NOT NULL, FK $\to$ `academic_periods(id)`)
  - `created_by` (`UUID`, FK $\to$ `user_profiles(id)`)
  - `algorithm_version` (`VARCHAR(30)`, NOT NULL, DEFAULT `'1.0.0'`)
  - `seed` (`BIGINT`, DEFAULT `20261022`)
  - `input_snapshot` (`JSONB`, NOT NULL, DEFAULT `'{}'::jsonb`)
  - `input_snapshot_hash` (`CHAR(64)`, NOT NULL)
  - `status` (`VARCHAR(20)`, NOT NULL, DEFAULT `'DRAFT'`, CHECK in `('DRAFT', 'SCHEDULING', 'REVIEW_REQUIRED', 'APPROVED', 'PUBLISHED', 'CANCELLED', 'SUPERSEDED')`)
  - `total_exams` (`INTEGER`, NOT NULL, DEFAULT 0), `scheduled_count` (`INTEGER`, NOT NULL, DEFAULT 0), `unassigned_count` (`INTEGER`, NOT NULL, DEFAULT 0)
- **Special Partial Unique Index**: `uq_published_run_per_period` enforces *at most one* `PUBLISHED` schedule run per academic period.

### 2.11 `schedule_assignments`
- **Purpose**: Allocation of an examination to a physical room across a discrete time window.
- **Columns**:
  - `id` (`UUID`, PK), `assignment_code` (`VARCHAR(64)`, NOT NULL, Format: `ASN-<exam_code>-<room_code>`)
  - `scheduling_run_id` (`UUID`, NOT NULL, FK $\to$ `scheduling_runs(id)`)
  - `exam_id` (`UUID`, NOT NULL, FK $\to$ `exams(id)`)
  - `room_id` (`UUID`, NOT NULL, FK $\to$ `rooms(id)`)
  - `start_time` (`TIMESTAMPTZ`, NOT NULL), `end_time` (`TIMESTAMPTZ`, NOT NULL, CHECK `end_time > start_time`)
  - `status` (`VARCHAR(20)`, NOT NULL, DEFAULT `'CONFIRMED'`, CHECK in `('CONFIRMED', 'REJECTED', 'SUPERSEDED')`)
- **Composite Unique Invariant**: `uq_sa_composite` (`id, scheduling_run_id, exam_id, room_id`).

### 2.12 `run_exam_students` & `assignment_students`
- **Purpose**: Frozen student cohort snapshot and individual seat assignments with composite relational integrity.
- **Composite FKs on `assignment_students`**:
  - `fk_asgn_sa_composite`: References `schedule_assignments(id, scheduling_run_id, exam_id, room_id)`
  - `fk_asgn_res_composite`: References `run_exam_students(id, scheduling_run_id, exam_id, student_id)`

### 2.13 `scheduling_decisions`, `schedule_events`, `audit_logs`
- **Purpose**: Algorithmic decision telemetry, lifecycle state transition events, and append-only audit trail.
- **Immutability Enforcement**: Protected by plpgsql triggers `prevent_modification_of_immutable_logs` preventing UPDATE or DELETE actions.

---

## 3. Schema Drift Analysis

Comparison between SQL migrations (`supabase/migrations/*.sql`), backend Pydantic models (`backend/models/*.py`), and live hosted Supabase PostgreSQL catalog confirms:
1. **Zero missing tables**: All 26 tables are present in the hosted database.
2. **Zero missing columns**: Every column in migrations matches database information schema.
3. **Zero constraint omissions**: All 51 foreign keys, 28 check constraints, and 33 unique constraints are active.
4. **Triggers verified**: All 4 immutability and user profile security triggers are compiled and armed.
5. **RLS status**: RLS is strictly enabled across 100% of tables (26 / 26).

