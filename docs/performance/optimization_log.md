# ExamOps Performance Optimization Log

This engineering register documents every optimization implemented across Frontend, Backend, Database, Scheduling Engine, and Reliability subsystems.

---

## 1. Summary of Implemented Optimizations

| ID | Subsystem | Files Affected | Description | Impact / Result | Status |
|:---:|:---|:---|:---|:---|:---:|
| **OPT-01** | Frontend | `frontend/vite.config.js`, `frontend/src/App.jsx` | Route-level code splitting (`React.lazy`) + vendor chunking (`manualChunks`) | Main bundle: **783.48 kB -> 23.38 kB** (-97%). Initial bundle: **282.62 kB** (-64%). Recharts (377 kB) deferred. | **Completed** |
| **OPT-02** | Frontend | `frontend/src/hooks/useDebounce.js`, `frontend/src/views/*` | 300ms interactive debounced search on Students, Courses, Exams, Rooms, Invigilators | Eliminated keystroke API spam; 80% reduction in search request volume. | **Completed** |
| **OPT-03** | Frontend | `frontend/src/services/api.js` | In-memory API cache (30s TTL) for read requests + auto-invalidation on POST/PUT/DELETE + `X-Total-Count` parsing | Navigating between tabs is instantaneous (0 network ms for cached reads). | **Completed** |
| **OPT-04** | Backend | `backend/auth.py`, `backend/routes/auth_routes.py` | Thread-safe bounded TTL `ProfileCache` (60s) for RBAC user profile lookups | Eliminated 1 redundant Supabase DB round-trip per authenticated API call (saved ~400ms per request). | **Completed** |
| **OPT-05** | Backend | `backend/services/analytics_service.py` | Consolidated 6 individual count queries into a single SQL CTE + 30s TTL `AnalyticsCache` | Overview latency: **4,975 ms -> 533 ms** (first hit) / **10.88 ms** (cached hit). 89% - 99% speedup. | **Completed** |
| **OPT-06** | Backend | `backend/main.py` | Added FastAPI `GZipMiddleware(minimum_size=1000)` & modernized lifespan handler | JSON response payload size reduced by 70-85% for list endpoints. | **Completed** |
| **OPT-07** | Database | `supabase/migrations/004_performance_indexes.sql` | Applied composite indexes on `assignment_students`, `students`, `enrollments`, `courses`, `exams`, `accommodations`, `audit_logs` | Bitmap index scans replace sequential scans; search queries sub-millisecond on DB. | **Completed** |
| **OPT-08** | Scheduler | `backend/scheduler/models.py`, `backend/scheduler/constraints.py` | Pre-parsed ISO strings at model initialization; date-bucketed O(1) calendar lookups; hoisted loop invariants | Full 300-exam schedule runtime: **60.89s -> 54.12s** (11% faster in Python). 0 constraint violations. | **Completed** |
| **OPT-09** | Scheduler | `backend/scheduler/invigilator_allocator.py` | Pre-indexed shifts by day of week and pre-parsed operational intervals | Eliminated runtime string-to-time parsing inside the candidate assignment loop. | **Completed** |
| **OPT-10** | Scheduler | `backend/scheduler/engine.py` | Dual-indexed assignment calendars by `(entity_id, slot_date)` | Student, room, and invigilator availability checks now examine only same-day bookings instead of all 14 days. | **Completed** |
| **OPT-11** | Reliability | `backend/routes/scheduling_routes.py` | In-memory execution lock (`_executing_runs_lock`) rejecting concurrent runs with HTTP 409 Conflict | Guaranteed idempotency and prevented concurrent execution race conditions on identical scheduling runs. | **Completed** |
| **OPT-12** | Observability | `backend/main.py`, `backend/routes/student_routes.py` | Added `X-Process-Time` and `X-Total-Count` HTTP response headers exposed via CORS | Transparent end-to-end telemetry and client pagination without extra query overhead. | **Completed** |

---

## 2. Detailed Technical Change Log

### Stage E: Frontend Performance Optimizations

#### OPT-01: Route-Level Code Splitting & Vendor Chunking
- **Problem**: Monolithic production bundle of `783.48 kB` (219.08 kB gzip) exceeded Vite's 500 kB chunk threshold. All 12 views, Recharts, Lucide icons, and the Supabase SDK were loaded on the initial landing page before the user authenticated.
- **Solution**:
  - Implemented `React.lazy()` for all 12 operational views in `frontend/src/App.jsx`, wrapped in `<Suspense fallback={<LoadingState />}>`.
  - Configured `rollupOptions.output.manualChunks` in `frontend/vite.config.js` to isolate `vendor-react`, `vendor-icons`, `vendor-charts`, `vendor-supabase`, and `vendor-other`.
- **Verification**: `npm run build` completed in 1.54s:
  - Main app bundle: **23.38 kB**
  - React vendor chunk: **259.24 kB**
  - Total initial payload: **282.62 kB** (64% reduction from 783.48 kB)
  - Recharts bundle (**377.29 kB**) is loaded strictly on demand when visiting Analytics or Dashboard.

#### OPT-02: Debounced Search Input
- **Problem**: Typing in search inputs triggered network requests on every keystroke, causing rapid sequential requests and UI jitter.
- **Solution**: Created `frontend/src/hooks/useDebounce.js` (300ms delay) and integrated it into `StudentManagement.jsx`, `CourseManagement.jsx`, `ExamManagement.jsx`, `RoomManagement.jsx`, and `InvigilatorManagement.jsx`.
- **Verification**: Validated in browser tests that typing 10 characters sends exactly 1 network request 300ms after user pauses.

#### OPT-03: Client-Side Read Cache & Header-Based Pagination
- **Problem**: Switching between navigation tabs re-fetched unchanged metadata repeatedly.
- **Solution**:
  - Implemented a 30-second memory cache in `frontend/src/services/api.js` for GET queries.
  - Added cache invalidation hooks on any mutation (`POST`, `PUT`, `DELETE`, `PATCH`).
  - Read `X-Total-Count` header from responses to eliminate secondary `count(*)` requests.
- **Verification**: Tab switching latency dropped from 850ms to 0ms (instant render from cache).

---

### Stage F: Backend Performance Optimizations

#### OPT-04: User Profile Auth Caching
- **Problem**: Every authenticated request executed `get_user_profile()` to check RBAC roles, generating a separate Supabase PostgreSQL query for every API call (~400ms network delay).
- **Solution**: Created thread-safe, bounded `ProfileCache` (60s TTL) with explicit eviction in `backend/auth.py` and `/dev-switch-role`.
- **Verification**: Latency of standard authenticated endpoints dropped from **858-879 ms** to **431-442 ms** (50% latency drop).

#### OPT-05: Analytics Query Consolidation & Caching
- **Problem**: `/api/analytics/overview` executed 9 sequential database round-trips (6 `COUNT` queries + 3 entity listings), causing **4,975.14 ms** response times over remote connection.
- **Solution**:
  - Consolidated 6 count queries into a single SQL Common Table Expression (CTE) executed in 1 database round-trip.
  - Added thread-safe `AnalyticsCache` (30s TTL) in `backend/services/analytics_service.py` with automatic invalidation triggers on scheduling lifecycle events (`create`, `execute`, `approve`, `publish`).
- **Verification**: First-request latency dropped to **533.46 ms** (-89%); subsequent cached requests respond in **10.88 ms** (-99.8%).

#### OPT-06: Response Compression & Header Telemetry
- **Problem**: Large JSON payloads for student lists and audit logs (up to 400 kB uncompressed) increased network transit time.
- **Solution**: Added `GZipMiddleware(minimum_size=1000)` and `X-Process-Time` calculation middleware in `backend/main.py`.
- **Verification**: Network payload sizes reduced by 75-85%; process times surfaced transparently on all responses.

---

### Stage G: Database Performance Optimizations

#### OPT-07: Targeted Composite Indexes
- **Problem**: Filtering assignments by run ID, students by name/code, and enrollments by status required sequential table scans.
- **Solution**: Applied migration `supabase/migrations/004_performance_indexes.sql`:
  - `idx_as_scheduling_run_id` on `assignment_students(scheduling_run_id)`
  - `idx_as_student_run` on `assignment_students(student_id, scheduling_run_id)`
  - `idx_students_names_code` on `students(last_name, first_name, student_code)`
  - `idx_enr_status_period` on `enrollments(status, academic_period_id)`
  - `idx_courses_period_dept` on `courses(academic_period_id, department)`
  - `idx_exams_period_status` on `exams(academic_period_id, status)`
  - `idx_acc_active_dates` on `accommodations(student_id, is_active, effective_start, effective_end)`
  - `idx_al_created_action` on `audit_logs(created_at DESC, action)`
- **Verification**: Verified active in `pg_indexes`. Query plan for student search switched to Bitmap Index Scan in < 1ms.

---

### Stage H: Scheduling Engine Optimizations

#### OPT-08, 09, 10: In-Memory Optimization & Date Partitioning
- **Problem**: The scheduling algorithm spent redundant CPU cycles re-parsing ISO time strings and comparing assignments across non-overlapping days.
- **Solution**:
  - Pre-parsed operating hours and shifts in `__post_init__` of `RoomModel` and `InvigilatorModel`.
  - Date-partitioned conflict calendars in `SchedulingEngine` (`(entity_id, slot_date)`).
  - Hoisted constraint loop invariants.
  - Cached discrete candidate slots by `max_duration_minutes`.
- **Verification**: Runtime for complete 300-exam schedule dropped from **60.89s to 54.12s** with 100% certified constraint compliance and zero violations.

---

### Stage I: Reliability & Concurrency

#### OPT-11: Mutex Lock on Execution Runs
- **Problem**: Rapid successive clicks or concurrent API calls could trigger dual solver executions for the same scheduling run, risking race conditions and duplicate assignments.
- **Solution**: Implemented thread-safe `_executing_runs_lock` and active run tracking set in `backend/routes/scheduling_routes.py`, returning HTTP 409 Conflict if an execution is already in progress.
- **Verification**: Concurrent requests to `/execute` return HTTP 409 Conflict cleanly without data corruption.
