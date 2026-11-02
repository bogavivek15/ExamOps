# ExamOps Full-Stack Bottleneck Analysis & Prioritization Register

**Date:** 2026-11-02  
**Author:** Principal Software Performance Engineer  
**Objective:** Systematically rank performance bottlenecks across Frontend, Backend, Database, and Scheduling Engine to guide high-impact optimizations without regression.

---

## 1. Bottleneck Ranking Matrix

| Rank | Subsystem | Bottleneck Identifier | Root Cause | Impact | Effort | Risk |
|:---:|:---|:---|:---|:---:|:---:|:---:|
| **1** | Backend / DB | **Sequential Analytics Queries** | `AnalyticsService.get_overview_metrics` fires 9 sequential queries across remote DB | 🔴 Critical (~5.0s latency) | Low | Low |
| **2** | Backend / Auth | **Redundant User Profile DB Lookups** | Every authenticated request queries `user_profiles` table, adding 1 unnecessary round-trip (400ms) | 🔴 Critical (doubles all API latency) | Low | Low |
| **3** | Scheduling | **Isoformat Parsing in Hot Loops** | Room operating hours & invigilator shifts parse ISO time strings millions of times during slot evaluation | 🔴 Critical (~60s runtime) | Medium | Very Low |
| **4** | Scheduling | **Unindexed Calendar Scans** | Student & room conflict checks scan across entire 2-week period rather than date-bucketed intervals | 🔴 High | Medium | Very Low |
| **5** | Frontend | **Monolithic Client Bundle** | `App.jsx` statically imports all 12 modules; bundle is 783 kB without code splitting | 🟠 High (Slow FCP/LCP) | Medium | Low |
| **6** | Frontend | **Un-debounced Table Search** | Typing in student/course search fires API calls on every keystroke | 🟠 High (API spam & DB contention) | Low | Low |
| **7** | Database | **Missing Run Index on Assignment Tables** | `assignment_students` lacks index on `scheduling_run_id`, slowing deletions and count aggregations | 🟠 High | Low | Very Low |
| **8** | Backend / HTTP | **Missing HTTP Response Compression** | FastAPI backend lacks GZip middleware for large JSON/CSV payloads | 🟡 Medium (High network transfer) | Low | Very Low |
| **9** | Backend / DB | **N+1 Exam Participant Subqueries** | `exam_routes.py` and `SchedulingService` calculate enrollments and requirements without optimal bulk joining | 🟡 Medium | Medium | Low |
| **10**| Frontend / Nav | **Cache Invalidation & Redundant Refetching** | Switching between tabs repeatedly refetches identical static metadata (rooms, invigilators, periods) | 🟡 Medium | Medium | Low |

---

## 2. In-Depth Root Cause & Remediation Strategy

### 2.1 Bottleneck 1: Sequential Overview Analytics Queries (4,975 ms)
- **Current Behavior:** `AnalyticsService.get_overview_metrics()` executes 9 discrete queries sequentially: `count(*) students`, `count(*) courses`, `count(*) exams`, `count(*) rooms`, `count(*) invigilators`, `count(*) accommodations`, `SELECT academic_period`, `SELECT scheduling_run`, `count(*) assignment_students`.
- **Root Cause:** Excessive round-trips over AWS-pooler connection (150-200ms ping each).
- **Remediation:** 
  1. Combine all master data scalar counts into a single consolidated SQL CTE or subquery expression.
  2. Implement an in-memory TTL cache (e.g., 60 seconds) with explicit cache invalidation when runs are executed or published.

### 2.2 Bottleneck 2: Redundant User Profile Verification on Every Request (858 ms)
- **Current Behavior:** `get_current_user` dependency in `backend/auth.py` queries `user_profiles` table on every single incoming HTTP request.
- **Root Cause:** Authentication verification makes an extra database trip before running the actual route query.
- **Remediation:**
  1. Introduce a thread-safe, bounded in-memory LRU/TTL cache (`ProfileCache`) with 60-second expiration.
  2. Invalidate cache on role changes (`/auth/dev-switch-role`) or profile updates.
  3. Keep fallback to database on cache miss.

### 2.3 Bottleneck 3 & 4: Scheduling Engine Inefficiencies (60.89s)
- **Current Behavior:** Full scheduling run takes 60.89s in-memory.
- **Root Cause:**
  1. `ConstraintChecker.check_room_availability` and `InvigilatorAllocator.allocate_invigilators` repeatedly execute `time.fromisoformat()` and `date.fromisoformat()` inside nested loops for each slot and room.
  2. `ConstraintChecker.check_student_non_overlap` checks all commitments for each student across the entire academic period, rather than filtering to the slot's specific date.
  3. `timedelta` calculations repeated for each commitment rather than once per participant.
- **Remediation:**
  1. Pre-parse and normalize operating hours, closures, and invigilator shifts into native `time` and `date` objects once during initialization.
  2. Bucket `student_calendar`, `room_calendar`, and `invigilator_calendar` by date: `calendar_by_date[(entity_id, date_val)]`.
  3. Compute `p_end = slot_start + timedelta(...)` once outside the commitment loop.

### 2.4 Bottleneck 5: Monolithic Client Bundle (783 kB)
- **Current Behavior:** Single bundle `index-*.js` of 783.48 kB (219.08 kB gzipped).
- **Root Cause:** All 12 operational views and heavy libraries (`recharts`, `lucide-react`) are synchronously imported at startup in `App.jsx`.
- **Remediation:**
  1. Replace synchronous imports in `App.jsx` with `React.lazy()` and wrap route transitions in `<Suspense fallback={<LoadingState />}>`.
  2. Configure `vite.config.js` with `build.rollupOptions.output.manualChunks` to split vendor dependencies:
     - `vendor-react`: `react`, `react-dom`, `react-router-dom`
     - `vendor-ui`: `lucide-react`
     - `vendor-charts`: `recharts`
     - `vendor-supabase`: `@supabase/supabase-js`

### 2.5 Bottleneck 6: Non-Debounced Interactive Search
- **Current Behavior:** In `StudentManagement.jsx`, `CourseManagement.jsx`, etc., changing `search` in `useEffect` fires an immediate API call on every keystroke.
- **Root Cause:** Missing debounce hook/timeout.
- **Remediation:**
  1. Implement a lightweight `useDebounce` hook (300ms delay).
  2. Only trigger `api.listStudents` and table reload when the debounced search value changes.

### 2.6 Bottleneck 7 & 8: Database Indexing & Response Compression
- **Current Behavior:** Full table scans on `assignment_students` when deleting or counting by `scheduling_run_id`. Responses sent uncompressed over HTTP.
- **Root Cause:** Migration 002 omitted index on `assignment_students(scheduling_run_id)`. FastAPI app lacks GZip middleware.
- **Remediation:**
  1. Add migration / index: `CREATE INDEX IF NOT EXISTS idx_as_scheduling_run_id ON assignment_students(scheduling_run_id);`.
  2. Add `CREATE INDEX IF NOT EXISTS idx_students_names ON students(first_name, last_name);`.
  3. Add `GZipMiddleware(minimum_size=1000)` to FastAPI in `backend/main.py`.

