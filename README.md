# ExamOps — Examination Operations & Intelligent Scheduling Platform

> *"Plan Smarter. Schedule Precisely. Operate With Confidence."*

[![Build & Test Status](https://img.shields.io/badge/Pytest-42%2F42%20Passing-57BE93.svg)](docs/testing.md)
[![Architecture](https://img.shields.io/badge/Architecture-FastAPI%20%7C%20React%20%7C%20PostgreSQL-56D6C2.svg)](docs/architecture.md)
[![Database](https://img.shields.io/badge/Database-26%20Tables%20%7C%20RLS%20Enforced-7CAAE5.svg)](docs/erd.md)
[![Constraints](https://img.shields.io/badge/Hard%20Constraints-0%20Violations-57BE93.svg)](docs/scheduling_algorithm.md)
[![AI Transparency](https://img.shields.io/badge/AI%20Prompts-Logged%20%26%20Disclosed-E8B66D.svg)](docs/ai_prompt_history.md)

---

## 1. Problem Statement & Operational Objective

Managing examinations across higher education institutions—handling thousands of enrolled students, hundreds of courses, complex physical facilities, invigilator work-hour limits, and specialized disability accommodations—is one of the most operationally critical undertakings an academic administration faces.

**ExamOps** addresses the end-to-end examination management lifecycle:
1. **Topological Master Data Ingestion:** Validates students, courses, enrollments, examination requirements, and facilities before scheduling.
2. **Conflict Graph Analytics:** Identifies co-enrolled student overlaps and builds conflict graphs to order examinations by scheduling difficulty.
3. **Deterministic Heuristic Scheduling:** Allocates examinations to collision-free time slots and rooms following the Seven Room-Splitting Invariants.
4. **Decision Telemetry & Root-Cause Attribution:** Explains every scheduling assignment and rejection with auditable constraint telemetry and structured reason codes (`CAPACITY_DEFICIT`, `STUDENT_CONFLICT`, `NO_INVIGILATOR_AVAILABLE`).
5. **Auditable Lifecycle Management:** Enforces immutable audit logging, non-recursive Row-Level Security, and atomic serialized publication with PostgreSQL advisory locks.

---

## 2. Core Application Capabilities & UI Walkthrough

The platform features 12 specialized operational modules accessible via a dark-first enterprise operations command center:

| Module | Core Functionality | Primary View Component |
|---|---|---|
| **01. Overview Dashboard** | Institution-wide KPIs, seat efficiency, upcoming exams, real-time metrics | [`OverviewDashboard.jsx`](frontend/src/views/OverviewDashboard.jsx) |
| **02. Scheduling Operations** | Timetable timeline, run execution, candidate slot telemetry, assignment inspection | [`SchedulingWorkspace.jsx`](frontend/src/views/SchedulingWorkspace.jsx) |
| **03. Exam Management** | Course associations, duration requirements, priority levels, scheduling history | [`ExamManagement.jsx`](frontend/src/views/ExamManagement.jsx) |
| **04. Student Management** | Student directory, course enrollments, personalized exam schedules | [`StudentManagement.jsx`](frontend/src/views/StudentManagement.jsx) |
| **05. Course & Enrollments** | Departmental course catalogs, active enrollments, cohort sizes | [`CourseManagement.jsx`](frontend/src/views/CourseManagement.jsx) |
| **06. Room & Facilities** | Venue capacities, maintenance closures, wheelchair accessibility features | [`RoomManagement.jsx`](frontend/src/views/RoomManagement.jsx) |
| **07. Invigilator Staffing** | Availability matrices, weekly workload tracking (8h/day, 25h/week caps) | [`InvigilatorManagement.jsx`](frontend/src/views/InvigilatorManagement.jsx) |
| **08. Accommodations** | Extended time multipliers, low-distraction spaces, privacy-redacted notes | [`AccommodationManagement.jsx`](frontend/src/views/AccommodationManagement.jsx) |
| **09. Exception Center** | Unassigned exam triage, constraint failure logs, corrective recommendations | [`ExceptionCenter.jsx`](frontend/src/views/ExceptionCenter.jsx) |
| **10. Analytics & Reports** | Seating reconciliation, invigilator workload distribution, CSV/JSON exports | [`AnalyticsReports.jsx`](frontend/src/views/AnalyticsReports.jsx) |
| **11. Audit & Activity** | Tamper-evident governance ledger with immutable change history | [`AuditActivity.jsx`](frontend/src/views/AuditActivity.jsx) |
| **12. Administration** | Academic periods, time-slot policies, institutional parameters | [`Administration.jsx`](frontend/src/views/Administration.jsx) |

### Key User Interface Visuals

```
docs/screenshots/
├── 01_dashboard.png                     (Overview dashboard metrics & KPIs)
├── 02_scheduling_workspace.png          (Scheduling timetable & slot evaluation)
├── 03_exception_center.png              (Decision telemetry & reason codes)
├── 04_accommodation_management.png      (Student accessibility & privacy masking)
├── 05_analytics_reports.png             (Reconciliation & seat utilization)
├── 06_audit_activity.png                (Immutable governance audit logs)
└── examops_brand_icon_and_favicon_preview.png
```

---

## 3. Technology Stack & Actual Package Versions

ExamOps utilizes a lightweight, modern stack free of black-box AI schedulers or heavy ORMs:

### Frontend
- **Framework:** React 19 (`19.3.1`) + Vite 8 (`8.3.5`)
- **Routing:** React Router 7 (`7.18.5`)
- **Styling:** Tailwind CSS (`3.4.17`) with dark-first enterprise tokens
- **Data Visualization & Icons:** Recharts (`3.10.1`), Lucide React (`1.66.0`)
- **Client SDK:** Supabase JavaScript Client (`2.118.0`)

### Backend
- **Framework:** Python 3.12+ with FastAPI (`0.115.0`) & Uvicorn (`0.30.6`)
- **Data Validation:** Pydantic (`2.9.2`) & Pydantic Settings (`2.5.2`)
- **Database Driver:** `psycopg2-binary` (`2.9.9`) with Threaded Connection Pooling
- **Authentication:** `python-jose` (`3.3.0`) & Supabase Python SDK (`2.8.2`)
- **Testing:** Pytest (`9.2.0`) & HTTPX (`0.27.2`)

### Database & Persistence
- **Engine:** PostgreSQL 16 (hosted via Supabase with PgBouncer connection pooler)
- **Security:** 26 relational tables with Row-Level Security (RLS) and immutability triggers
- **Distributed Concurrency:** PostgreSQL 64-bit advisory locks (`pg_try_advisory_lock`)

---

## 4. Architecture Overview

```
                      +-----------------------------------+
                      |      React 19 + Vite Frontend     |
                      |  12 Operational Product Modules   |
                      +-----------------+-----------------+
                                        |  REST API / JWT
                                        v
                      +-----------------+-----------------+
                      |       FastAPI Backend API         |
                      |  - Role-Based Access Control      |
                      |  - 11 Domain Route Controllers    |
                      |  - 10 Business Services           |
                      |  - PostgreSQL Advisory Lock       |
                      +--------+-----------------+--------+
                               |                 |
            Solve Algorithm    |                 |  SQL Queries & Pooling
                               v                 v
+------------------------------+----+   +--------+-------------------------+
| Pure Python Scheduling Engine     |   | PostgreSQL 16 (Supabase)         |
| - Student Conflict Graph Builder  |   | - 24 Normalized Relational Tables|
| - Best-Fit Decreasing Room Solver |   | - Row-Level Security Policies    |
| - Seven Room-Splitting Invariants |   | - Immutable Audit Log Triggers   |
| - Staffing & Workload Allocator   |   | - Frozen Participation Snapshots |
| - Constraint Telemetry Engine     |   | - Threaded Connection Pool (16)  |
+-----------------------------------+   +----------------------------------+
```

---

## 5. Repository Directory Structure

```text
ExamOps/
├── .dockerignore
├── .env.example                         (Environment configuration template)
├── .gitignore
├── AGENTS.md                            (Definitive Master Engineering Spec)
├── Dockerfile                           (Containerized backend deployment)
├── README.md                            (Primary setup & evaluation guide)
├── render.yaml                          (Render FastAPI deployment spec)
├── requirements.txt                     (Python dependencies)
├── backend/
│   ├── auth.py                          (JWT verification & RBAC resolution)
│   ├── config.py                        (Pydantic application settings)
│   ├── database.py                      (Threaded connection pool & URL masking)
│   ├── main.py                          (FastAPI application & CORS)
│   ├── models/schemas.py                (Pydantic request/response models)
│   ├── routes/                          (11 REST router modules)
│   ├── scheduler/                       (9 deterministic solver modules)
│   ├── services/                        (10 domain business services)
│   └── tests/                           (5 pytest database integrity suites)
├── data/
│   ├── csv/                             (17 synthetic CSV datasets)
│   ├── json/                            (17 synthetic JSON datasets)
│   ├── sql/seed_data.sql                (6.2 MB bulk SQL insert script)
│   ├── ground_truth.csv                 (5 isolated negative scenarios)
│   ├── ground_truth.json                (Machine-readable ground truth)
│   └── manifest.json                    (Canonical entity counts & SHA-256)
├── docs/
│   ├── ai_prompt_history.md             (Transparent AI prompt ledger)
│   ├── ai_prompts/                      (Archived full prompt texts)
│   ├── architecture.md                  (System architecture & ADRs DEC-001..006)
│   ├── assumptions.md                   (26 institutional configuration assumptions)
│   ├── business_rules.md                (Domain constraints & defaults)
│   ├── candidate_interview_defense.md   (Technical walkthrough & interview guide)
│   ├── data_dictionary.md               (Field-level specifications for all tables)
│   ├── design_system.md                 (Tokens, color palette, components)
│   ├── erd.md                           (Entity relationship diagram & cardinality)
│   ├── evaluation.md                    (Performance, concurrency & latency metrics)
│   ├── implementation_plan.md           (Implementation roadmap)
│   ├── known_issues_and_limitations.md  (Conflict graph density & baseline findings)
│   ├── permissions.md                   (RBAC matrix across 5 roles)
│   ├── requirements.md                  (Requirements register)
│   ├── requirements_traceability.md     (Requirement-to-code traceability)
│   ├── scheduling_algorithm.md          (Invariants, worked examples & proof)
│   ├── screenshots/                     (6 verified UI desktop screenshots)
│   ├── security.md                      (Data privacy, RLS policies, audit)
│   ├── source/                          (4 authoritative problem & FAQ documents)
│   ├── source_manifest.md               (Synthetic data provenance specification)
│   ├── technical_risks.md               (Risk register & mitigations)
│   ├── testing.md                       (Automated testing strategy)
│   └── validation_report.md             (Database validation & integrity report)
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── public/                          (Favicon & icons)
│   └── src/
│       ├── App.jsx                      (Lazy-loaded router for 12 modules)
│       ├── components/common/           (7 canonical UI components)
│       ├── context/AuthContext.jsx      (RBAC authentication context)
│       ├── services/api.js              (33 REST API client methods)
│       ├── styles/theme.css             (Outskill Electric Lime #B8EF43 theme)
│       └── views/                       (12 operational module views)
├── generator/
│   ├── config.py                        (Seed 20261022 & profile definitions)
│   ├── exporters.py                     (CSV, JSON, and SQL seed generator)
│   ├── generate.py                      (Deterministic synthetic generator)
│   └── negative_scenarios.py            (5 mandatory negative anomaly injector)
├── scripts/
│   ├── apply_and_test_database.py       (Schema setup & verification harness)
│   ├── apply_cloud_migrations.py        (Cloud database migration runner)
│   ├── load_cloud_baseline.py           (Cloud seed data loader)
│   ├── test_scheduler.py                (Core pytest scheduling engine suite)
│   ├── test_synthetic_data.py           (2-run reproducibility suite)
│   ├── browser_acceptance_eight_modules.js (Headless Puppeteer test suite)
│   ├── analyze_conflict_graph.py        (Graph density inspection tool)
│   ├── inspect_scheduling_details.py    (Assignment & telemetry inspector)
│   └── database/                        (4 database validation scripts)
├── supabase/migrations/                 (5 PostgreSQL schema migrations)
└── tests/
    ├── test_backend_api.py              (9 API endpoint test suites)
    ├── test_distributed_concurrency.py  (Advisory lock mutual exclusion tests)
    └── test_role_revocation.py          (RBAC session downgrade tests)
```

---

## 6. Prerequisites

- **Python:** Version `3.12` or higher
- **Node.js:** Version `20.x` or `22.x` (with `npm 10+`)
- **Database:** PostgreSQL 15/16 (or Supabase Cloud instance)

---

## 7. Backend Installation & Startup

1. **Navigate to workspace root and configure virtual environment:**
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL/Supabase database URL and JWT credentials
   ```

4. **Start the FastAPI backend server:**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Interactive Swagger documentation will be available at `http://localhost:8000/docs`.

---

## 8. Frontend Installation & Startup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```
   The application UI will run at `http://localhost:5173`.

3. **Build for production:**
   ```bash
   npm run build
   ```

---

## 9. Supabase Database Configuration & Migrations

To apply the database schema against a local or remote PostgreSQL instance:

```bash
# Apply migrations 001 through 005 sequentially:
python scripts/apply_and_test_database.py
```

The 5 migration files in `supabase/migrations/` establish:
- `001_core_master_and_security.sql`: Core tables, immutability triggers, and helper functions.
- `002_scheduling_engine.sql`: Scheduling runs, assignments, decisions, and participation snapshots.
- `003_rls_and_policies.sql`: Row-Level Security policies restricting clinical notes.
- `004_performance_indexes.sql`: Targeted composite B-tree indexes.
- `005_cleanup_redundant_indexes.sql`: Eliminates redundant prefix indexes.

---

## 10. Synthetic Data Generation

To generate the full baseline dataset from scratch using fixed seed `20261022`:

```bash
python generator/generate.py
```

This generates:
- **5,000 Students** (`STU-000001` to `STU-005000`)
- **300 Examinations** (`EXAM-2026-000001` to `EXAM-2026-000300`)
- **100 Rooms** (`ROOM-000001` to `ROOM-000100`)
- **200 Invigilators** (`INV-000001` to `INV-000200`)
- **25,044 Enrollments**, **1,200 Availabilities**, **301 Accommodations**
- Outputs formatted into `data/csv/`, `data/json/`, and `data/sql/seed_data.sql`.

---

## 11. Reproducibility Verification

Per Problem Statement §10, run the two-run reproducibility verification:

```bash
python scripts/test_synthetic_data.py
```

**Verification Mechanism & Actual Execution Output:**
```text
=== Step 1: Testing Reproducibility across Independent Runs ===
Generating ExamOps dataset: profile='full', seed=20261022 (5000 students, 300 exams, 100 rooms, 200 invigilators)
  ✓ 17 canonical tables + 5 ground truth fixtures: SHA-256 Hashes 100% MATCH across Runs 1 and 2
=== Step 2: In-Memory Referential Integrity Verification ===
  ✓ All 25,044 enrollments, 300 exams, 107 requirements, 100 rooms, and 301 accommodations reference valid parents
=== Step 3: Identifier Format Verification ===
  ✓ All student, exam, room, and invigilator codes strictly conform to canonical regex patterns
=== Step 4: Loading SQL Seed into PostgreSQL & Reconciling Counts ===
  ℹ Disposable test container 'examops-db-test' is not running.
  ℹ Per Database Safety Policy, Step 4 was NOT RUN against production Supabase.
  ✓ Steps 1–3 (Reproducibility, Referential Integrity, Deterministic IDs) VERIFIED.
```

---

## 12. Automated Testing (42-Test Pytest Suite)

The automated test suite contains **exactly 42 test cases** covering database integrity, RBAC, API endpoints, distributed locking, and scheduler invariants:

```bash
python -m pytest backend/tests tests scripts/test_scheduler.py -v
```

### Breakdown of the 42 Tests

| Test Module | Test Count | Scope |
|---|---|---|
| `backend/tests/test_database_integrity.py` | 4 tests | Entity counts, PK patterns, NOT NULL columns, audit immutability triggers |
| `backend/tests/test_duplicate_detection.py` | 2 tests | Unique business codes, composite relationship uniqueness |
| `backend/tests/test_rbac_integrity.py` | 3 tests | Unauthenticated rejection, learner route protection, accommodation masking |
| `backend/tests/test_referential_integrity.py` | 3 tests | FK cascades, composite keys on assignments, snapshot total consistency |
| `backend/tests/test_scheduling_integrity.py` | 5 tests | Zero student overlaps, zero room double-bookings, capacity limits, invigilator caps |
| `tests/test_backend_api.py` | 9 tests | Health check, auth, master data CRUD, clinical privacy, scheduling run workflow, exports |
| `tests/test_distributed_concurrency.py` | 5 tests | PostgreSQL advisory lock mutual exclusion, multi-process isolation, crash safety |
| `tests/test_role_revocation.py` | 7 tests | Role downgrades, deactivation, cache TTL, invalid JWT signatures |
| `scripts/test_scheduler.py` | 4 tests | Conflict graph heuristics, 7 room-splitting invariants, **5 negative scenarios**, full baseline |
| **TOTAL** | **42 tests** | **100% Passing (0 failures, 0 skips)** |

```text
================== 42 passed, 1 warning in 340.28s (0:05:40) ==================
```

---

## 13. Core Workflow Demonstration Steps

To walk through the complete examination scheduling operations workflow:

1. **Step 1: Data Initialization**
   - Confirm master data in `data/csv/` or run `python generator/generate.py`.
2. **Step 2: Start Services**
   - Start backend (`uvicorn backend.main:app --port 8000`) and frontend (`npm run dev`).
3. **Step 3: Open Scheduling Operations Center**
   - Navigate to `http://localhost:5173/scheduling`.
4. **Step 4: Execute a Scheduling Run**
   - Click **"Create Run"** and select the active period.
   - Click **"Execute Run"**; the backend acquires the advisory lock and runs the deterministic solver in ~4 seconds.
5. **Step 5: Inspect Decisions & Room Splits**
   - View scheduled assignments on the visual timetable. Click any examination card to inspect assigned rooms, seated students, and invigilator ratios.
6. **Step 6: Investigate Unassigned Examinations**
   - Navigate to **Exception Center** (`/exceptions`) to view structured failure reason codes (`CAPACITY_DEFICIT`, `STUDENT_CONFLICT`).
7. **Step 7: Approve and Publish**
   - Click **"Approve Schedule"** then **"Publish Schedule"**. The system executes an atomic row-locked transaction marking previous published schedules as `SUPERSEDED`.
8. **Step 8: Export Schedule**
   - Navigate to **Analytics & Reports** (`/analytics`) to download timetable CSV and JSON exports.

---

## 14. Empirical Results & Known Limitations

For complete details, see [`docs/known_issues_and_limitations.md`](docs/known_issues_and_limitations.md).

### Baseline Scheduling Result
- **Scheduled Examinations:** **81 examinations** across 317 room assignments (100% capacity in available sequential slots).
- **Unassigned Examinations:** **219 examinations** (all fully explained with telemetry and reason codes).

### Mathematical Cause (Conflict Graph Density)
Using `python scripts/analyze_conflict_graph.py`, we measured the student co-enrollment graph:
- Total Exams: 300
- Total Conflict Edges: 44,410 out of 44,850 maximum possible pairs (**Density: 0.990**).
- Average Conflict Degree: 296.1 out of 299.

Because synthetic students have broad cross-departmental enrollments, virtually every examination conflicts with every other examination. Under the strict hard constraint `STUDENT_NON_OVERLAP`, only ~1 exam can run at any given moment. In a 12-day window (08:00–18:00), there are only ~69 to 81 sequential non-overlapping time slots. ExamOps completely saturated every available slot without violating any hard constraints.

---

## 15. Using the CSV and JSON Exports

Pre-generated synthetic datasets and exports are available directly in the repository:
- **CSV Datasets:** Located in [`data/csv/`](data/csv/) (17 tabular files).
- **JSON Datasets:** Located in [`data/json/`](data/json/) (17 structured JSON files).
- **SQL Seed File:** Located at [`data/sql/seed_data.sql`](data/sql/seed_data.sql).
- **Live Timetable Export via API:**
  - `GET /api/exports/timetable.csv` $\to$ Returns confirmed schedule with exam code, course, slot, venue, and invigilator.
  - `GET /api/exports/timetable.json` $\to$ Returns full hierarchical assignment objects.

---

## 16. Submission Credentials & Verification Statement

This repository constitutes the complete submission for the YottaFlex AI Candidate Project:
- **Repository:** `https://github.com/bogavivek15/ExamOps.git`
- **Transparent AI Usage:** See [`docs/ai_prompt_history.md`](docs/ai_prompt_history.md) for full prompt ledger and autonomous execution disclosure.
- **Data Provenance:** See [`docs/source_manifest.md`](docs/source_manifest.md) for synthetic data verification.
- **Candidate Defense:** See [`docs/candidate_interview_defense.md`](docs/candidate_interview_defense.md) for architecture defense and walkthrough notes.
