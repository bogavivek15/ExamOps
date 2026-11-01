# ExamOps — Complete Module Functionality Guide

This guide documents each of the 12 core operational modules of ExamOps based on the real implementation across frontend views, backend FastAPI routes, PostgreSQL tables, and business logic contracts.

---

## Table of Contents
1. [Module 1 — Overview Dashboard](#module-1--overview-dashboard)
2. [Module 2 — Scheduling Operations Workspace](#module-2--scheduling-operations-workspace)
3. [Module 3 — Examination Management](#module-3--examination-management)
4. [Module 4 — Student Management](#module-4--student-management)
5. [Module 5 — Course & Enrollment Management](#module-5--course--enrollment-management)
6. [Module 6 — Room & Venue Management](#module-6--room--venue-management)
7. [Module 7 — Invigilator Management](#module-7--invigilator-management)
8. [Module 8 — Accommodation Management](#module-8--accommodation-management)
9. [Module 9 — Exception Center](#module-9--exception-center)
10. [Module 10 — Analytics & Reports](#module-10--analytics--reports)
11. [Module 11 — Audit & Activity](#module-11--audit--activity)
12. [Module 12 — Administration & Governance](#module-12--administration--governance)

---

## Module 1 — Overview Dashboard

### 1. Purpose
Provides institutional leadership and examination officers with a unified operational command view of current semester readiness, active academic periods, resource utilization, and scheduling progress.

### 2. Problem It Solves
Academic administrators previously lacked a single source of truth for examination metrics, relying on disconnected spreadsheets and manual status reports from faculty departments.

### 3. Who Uses It
- Academic Administrators (Deans, Vice-Provosts)
- Examination Directorate Officers
- Department Heads & Operations Directors

### 4. Data It Reads
- Active academic period metadata (`academic_periods`)
- Master dataset counts (`students`, `courses`, `exams`, `rooms`, `invigilators`, `accommodations`)
- Most recent scheduling run metrics (`scheduling_runs`)
- Open diagnostic issues count (`validation_issues`)

### 5. Data It Creates or Modifies
Read-only operational dashboard. Does not mutate database records directly.

### 6. Backend API Endpoints
- `GET /api/analytics/overview`: Aggregates institutional entity counts, latest run metrics, and completion statistics.

### 7. Database Tables Involved
- `academic_periods`, `students`, `courses`, `exams`, `rooms`, `invigilators`, `accommodations`, `scheduling_runs`, `validation_issues`

### 8. Important Buttons and Actions
- **Launch Scheduling Workspace**: Direct navigation shortcut to Module 2 to trigger or inspect timetables.
- **Academic Period Context Header**: Displays current active term (`Fall 2026 / TERM-2026-02`) and system health.
- **Role Switcher Dropdown**: Allows toggling between simulated operator perspectives.

### 9. Expected Successful Result
Displays high-level KPI tiles (Total Students: 5,000; Courses: 150; Exams: 300; Rooms: 100; Proctors: 200; Accommodations: 301), active semester dates, scheduling completion percentage, and active run status (`PUBLISHED`).

### 10. Possible Errors and Edge Cases
- **No Active Academic Period**: Displays fallback "No Active Semester" banner if `is_active = FALSE` across all terms.
- **Backend Offline / Database Disconnected**: Renders red error banner with a manual "Retry" button.

---

## Module 2 — Scheduling Operations Workspace

### 2.1 Purpose
The central operations hub for creating, solving, inspecting, approving, and publishing examination timetables with full algorithmic telemetry.

### 2.2 Problem It Solves
Replaces black-box solvers and manual scheduling with an explainable engine where officers can inspect individual candidate scores, room allocations, proctor assignments, and constraint passes/failures.

### 2.3 Who Uses It
- Examination Officers
- Academic Scheduling Coordinators
- System Administrators

### 2.4 Data It Reads
- Run catalog and historical runs (`scheduling_runs`)
- Schedule assignments (`schedule_assignments`, `rooms`, `exams`)
- Seated student snapshot (`assignment_students`, `run_exam_students`)
- Proctor staffing records (`assignment_invigilators`, `invigilators`)
- Algorithmic decision telemetry records (`scheduling_decisions`)

### 2.5 Data It Creates or Modifies
- Inserts new `scheduling_runs` in `DRAFT` status with frozen `input_snapshot_hash`.
- Generates `schedule_assignments`, `assignment_students`, `assignment_invigilators`, and `scheduling_decisions`.
- Updates run status: `DRAFT` $\rightarrow$ `SCHEDULING` $\rightarrow$ `COMPLETED` $\rightarrow$ `APPROVED` $\rightarrow$ `PUBLISHED`.

### 2.6 Backend API Endpoints
- `GET /api/scheduling/runs`: Lists all historical runs with completion metrics.
- `POST /api/scheduling/runs`: Creates new scheduling run with seed and algorithm version.
- `POST /api/scheduling/runs/{id}/execute`: Triggers the deterministic heuristic scheduling solver.
- `GET /api/scheduling/runs/{id}/assignments`: Retrieves confirmed room and timeslot allocations.
- `GET /api/scheduling/runs/{id}/decisions`: Retrieves decision telemetry records and reason codes.
- `POST /api/scheduling/runs/{id}/approve`: Approves schedule for institutional publication.
- `POST /api/scheduling/runs/{id}/publish`: Atomically publishes schedule via Supabase stored procedure.

### 2.7 Database Tables Involved
- `scheduling_runs`, `run_exam_students`, `schedule_assignments`, `assignment_students`, `assignment_invigilators`, `scheduling_decisions`, `schedule_events`, `audit_logs`

### 2.8 Important Buttons and Actions
- **+ New Run**: Opens modal to configure seed (`20261022`) and algorithm version.
- **Execute Solver**: Runs the multi-pass greedy algorithm against cloud Supabase.
- **Approve Schedule**: Advances run status from `COMPLETED` to `APPROVED`.
- **Publish Timetable**: Executes row-locked stored procedure `publish_schedule_run()`.
- **Inspect (Telemetry Drawer)**: Opens detailed side drawer displaying candidate slot evaluations, penalty scoring breakdown, and constraint rejection reasons.

### 2.9 Expected Successful Result
Generates certified conflict-free timetable assignments, renders confirmed rooms and proctors in the table, displays decision telemetry for every exam, and allows atomic publication.

### 2.10 Possible Errors and Edge Cases
- **Uncertified Run Publication Attempt**: Blocked if independent validator detected hard-constraint violations.
- **Double Publication Collision**: Prevented by database partial unique index (`uq_published_run_per_period`) and stored-procedure `FOR UPDATE` row lock.
- **Insufficient Permissions**: HTTP 403 Forbidden displayed gracefully if a Learner attempts to create or execute a run.

---

## Module 3 — Examination Management

### 3.1 Purpose
Manages the institutional catalog of official course examinations, testing durations, equipment prerequisites, and cohort registrations.

### 3.2 Problem It Solves
Prevents scheduling misconfigurations by ensuring that duration requirements, technical equipment needs (e.g., computer terminals, lab benches), and class priorities are formally codified before solver execution.

### 3.3 Who Uses It
- Examination Directorate Staff
- Department Curriculum Officers
- Academic Registrars

### 3.4 Data It Reads
- Examinations directory (`exams`)
- Associated course details (`courses`)
- Student enrollment counts per exam (`enrollments`)
- Special requirements (`exam_requirements`)

### 3.5 Data It Creates or Modifies
Creates and updates examination records, baseline durations, priorities, and physical equipment requirements.

### 3.6 Backend API Endpoints
- `GET /api/exams`: Paginated catalog with keyword search and lifecycle status filtering.
- `GET /api/exams/{id}`: Full examination profile.
- `GET /api/exams/{id}/requirements`: Required equipment and room features.

### 3.7 Database Tables Involved
- `exams`, `courses`, `enrollments`, `exam_requirements`, `equipment_types`

### 3.8 Important Buttons and Actions
- **Search Exams**: Instant client/server keyword search filtering across exam codes, titles, and course codes.
- **Status Filter**: Dropdown filtering (`DRAFT`, `READY_FOR_SCHEDULING`, `SCHEDULED`, `COMPLETED`).
- **View Details**: Opens drawer displaying course syllabus association, duration, and hardware requirements.

### 3.9 Expected Successful Result
Displays 300 examinations with deterministic codes (`EXAM-2026-000001` to `EXAM-2026-000300`), course titles, duration badges, and enrolled student counts.

### 3.10 Possible Errors and Edge Cases
- **Missing Course Linkage**: Foreign key constraint (`ON DELETE RESTRICT`) prevents orphan exams.
- **Zero Enrolled Students**: Flagged with an informative warning indicator in the details drawer.

---

## Module 4 — Student Management

### 4.1 Purpose
Maintains student registration master data, academic progression levels, course enrollment records, and personalized examination timetables.

### 4.2 Problem It Solves
Ensures that each student receives an individual, conflict-free examination itinerary and that accommodations are accurately tracked without violating medical privacy.

### 4.3 Who Uses It
- Registrar Operations
- Student Advisors & Counselors
- Students / Learners (read-only self perspective)

### 4.4 Data It Reads
- Student profiles (`students`)
- Course enrollments (`enrollments`, `courses`)
- Active accommodations summary (`accommodations`)
- Published examination seating assignments (`assignment_students`, `schedule_assignments`)

### 4.5 Data It Creates or Modifies
Updates student profile information, academic progression status, and program affiliations.

### 4.6 Backend API Endpoints
- `GET /api/students`: Paginated student registry with search and department filtering.
- `GET /api/students/{id}`: Detailed student profile.
- `GET /api/students/{id}/schedule`: Individual examination timetable and assigned desks.

### 4.7 Database Tables Involved
- `students`, `enrollments`, `courses`, `accommodations`, `assignment_students`, `schedule_assignments`, `rooms`

### 4.8 Important Buttons and Actions
- **Search Registry**: Search by student ID (`STU-000001`), first name, last name, or email.
- **Timetable Inspection**: Opens drawer rendering the student's personal exam itinerary with dates, times, rooms, and seat numbers.

### 4.9 Expected Successful Result
Renders 5,000 student records with pagination; clicking a student reveals their enrolled exams and confirmed desk locations for published runs.

### 4.10 Possible Errors and Edge Cases
- **Unscheduled Exams**: If an exam is unassigned, the student's timetable shows "Awaiting Scheduling" rather than an erroneous or broken timeslot.

---

## Module 5 — Course & Enrollment Management

### 5.1 Purpose
Oversees university course catalogs, department ownership, credit values, and active student enrollment rosters.

### 5.2 Problem It Solves
Solves the challenge of student-cohort co-enrollment mapping, which forms the mathematical basis for the Conflict Graph.

### 5.3 Who Uses It
- Curriculum Managers
- Department Chairs
- Academic Operations

### 5.4 Data It Reads
- Course master records (`courses`)
- Active student enrollments (`enrollments`, `students`)
- Department metadata

### 5.5 Data It Creates or Modifies
Registers new course offerings, updates credit hours, and maintains student-course enrollment rosters.

### 5.6 Backend API Endpoints
- `GET /api/courses`: Lists course offerings with department and credit counts.
- `GET /api/courses/{id}`: Course profile.
- `GET /api/enrollments`: Course class lists and student membership.

### 5.7 Database Tables Involved
- `courses`, `enrollments`, `students`, `academic_periods`

### 5.8 Important Buttons and Actions
- **Department Filter**: Filter courses by academic department (e.g., Computer Science, Mathematics).
- **View Class Roster**: Opens drawer listing all enrolled students with registration status.

### 5.9 Expected Successful Result
Displays 150 accredited courses with enrolled cohort counts (totaling 25,044 enrollments).

### 5.10 Possible Errors and Edge Cases
- **Duplicate Student Enrollment**: Database unique constraint `uq_enr_student_course_period` strictly prevents a student from being enrolled twice in the same course term.

---

## Module 6 — Room & Venue Management

### 6.1 Purpose
Manages physical campus examination venues, seating capacities, wheelchair accessibility, AV equipment, and maintenance blackout windows.

### 6.2 Problem It Solves
Prevents venue overcrowding, equipment mismatches, and compliance failures by verifying desk capacity and physical accessibility before assigning exams.

### 6.3 Who Uses It
- Facilities & Campus Logistics
- Examination Officers
- Accessibility Coordinators

### 6.4 Data It Reads
- Venue catalog (`rooms`)
- Effective capacities (`room_capacities`)
- Installed equipment inventory (`room_equipment`, `equipment_types`)
- Operating windows and closures (`room_availabilities`)

### 6.5 Data It Creates or Modifies
Registers new venues, updates effective examination desk caps, logs equipment installations, and records temporary room closures.

### 6.6 Backend API Endpoints
- `GET /api/rooms`: Paginated venues list with accessibility and capacity filters.
- `GET /api/rooms/{id}`: Detailed room profile with equipment and blackout dates.

### 6.7 Database Tables Involved
- `rooms`, `room_capacities`, `equipment_types`, `room_equipment`, `room_availabilities`

### 6.8 Important Buttons and Actions
- **Accessibility Filter**: Toggle to isolate certified wheelchair-accessible venues.
- **Venue Inspection Drawer**: Displays floor, building, exam desk capacity, installed hardware, and operational hours.

### 6.9 Expected Successful Result
Displays 100 campus rooms with distinct codes (`ROOM-000001` to `ROOM-000100`), exam desk capacities, and accessibility badges.

### 6.10 Possible Errors and Edge Cases
- **Exam Outside Operating Hours**: Solver rejects candidate slots falling within recorded `room_availabilities` closures.

---

## Module 7 — Invigilator Management

### 7.1 Purpose
Coordinates proctoring staff, department affiliations, individual availability schedules, and maximum daily/weekly workload caps.

### 7.2 Problem It Solves
Eliminates proctor double-booking and labor regulation breaches by tracking proctor shift hours and enforcing a maximum 1:30 student-to-proctor ratio.

### 7.3 Who Uses It
- Invigilation Roster Managers
- HR / Staffing Coordinators
- Teaching Assistants & Faculty

### 7.4 Data It Reads
- Invigilator directory (`invigilators`)
- Availability calendars (`availabilities`)
- Scheduled shift assignments (`assignment_invigilators`, `schedule_assignments`)

### 7.5 Data It Creates or Modifies
Maintains proctor profiles, availability periods, and committed shift assignments.

### 7.6 Backend API Endpoints
- `GET /api/invigilators`: Paginated proctor list with department and workload metrics.
- `GET /api/invigilators/{id}`: Proctor profile.
- `GET /api/invigilators/{id}/schedule`: Assigned exam supervision shifts and room locations.

### 7.7 Database Tables Involved
- `invigilators`, `availabilities`, `assignment_invigilators`, `schedule_assignments`

### 7.8 Important Buttons and Actions
- **Search Staff**: Search proctors by name, code (`INV-000001`), or department.
- **View Shift Roster**: Opens drawer showing confirmed proctoring assignments and assigned roles (PRIMARY / SECONDARY).

### 7.9 Expected Successful Result
Displays 200 active invigilators with workload caps (e.g., 6h/day, 20h/week) and shift counts.

### 7.10 Possible Errors and Edge Cases
- **Workload Saturation**: If a proctor reaches maximum hours, the engine automatically selects another qualified staff member.

---

## Module 8 — Accommodation Management

### 8.1 Purpose
Administers student accessibility requirements, extra time allowances, certified venue needs, and confidential medical documentation.

### 8.2 Problem It Solves
Guarantees full institutional compliance with accessibility laws (ADA, Equality Act) while protecting sensitive student diagnostic records under FERPA/GDPR privacy guidelines.

### 8.3 Who Uses It
- Disability Support Services Officers
- Authorized Examination Officers
- Students (viewing only their own accommodations)

### 8.4 Data It Reads
- Accommodation records (`accommodations`)
- Confidential clinical evaluations (`accommodation_notes`)
- Student directory (`students`)

### 8.5 Data It Creates or Modifies
Approves accommodation requests, sets extra time minutes, assigns venue feature requirements, and stores encrypted clinical evaluation notes.

### 8.6 Backend API Endpoints
- `GET /api/accommodations`: Paginated list of active student accommodations.
- `GET /api/accommodations/{id}/notes`: Retrieves clinical documentation (decrypted for Admins, masked with `[REDACTED]` for Learners).

### 8.7 Database Tables Involved
- `accommodations`, `accommodation_notes`, `students`

### 8.8 Important Buttons and Actions
- **Type Filter**: Filter by `EXTENDED_TIME`, `ACCESSIBLE_ROOM`, `LOW_DISTRACTION`, or `SPECIAL_EQUIPMENT`.
- **View Clinical Notes**: Opens drawer displaying clinical documentation with privacy indicators.

### 8.9 Expected Successful Result
Displays 301 verified accommodations; administrators see complete clinical notes, while unprivileged roles see redacted confidentiality notices.

### 8.10 Possible Errors and Edge Cases
- **Expired Accommodation**: The engine filters by `CURRENT_DATE BETWEEN effective_start AND effective_end` so expired accommodations do not affect current scheduling runs.

---

## Module 9 — Exception Center

### 9.1 Purpose
A dedicated investigation center for analyzing unscheduled examinations, constraint violations, and resource bottlenecks.

### 9.2 Problem It Solves
Prevents silent scheduling failures. When an examination cannot be scheduled, the Exception Center provides actionable diagnostic telemetry explaining why every single evaluated slot was rejected.

### 9.3 Who Uses It
- Examination Directorate Officers
- Academic Policy Review Committees
- Scheduling Problem Solvers

### 9.4 Data It Reads
- Hard-constraint violations (`validation_issues`)
- Unassigned examination decisions (`scheduling_decisions`)
- Cohort sizes and candidate slot evaluations

### 9.5 Data It Creates or Modifies
Logs administrative corrective actions and exception resolution notes.

### 9.6 Backend API Endpoints
- `GET /api/scheduling/runs/{id}/issues`: Independent validation issues.
- `GET /api/scheduling/runs/{id}/decisions?is_assigned=false`: Unassigned examination telemetry records.

### 9.7 Database Tables Involved
- `validation_issues`, `scheduling_decisions`, `exams`, `scheduling_runs`

### 9.8 Important Buttons and Actions
- **Run Selector**: Choose which scheduling run to diagnose.
- **Inspect Exception**: Opens drawer showing evaluated slot counts, primary reason codes (`STUDENT_CONFLICT`), and suggested corrective actions.

### 9.9 Expected Successful Result
Clearly explains why 219 examinations were unassigned in the baseline run (e.g., student conflict graph saturation across 192 evaluated candidate slots) and confirms 0 hard constraint breaches in certified assignments.

### 9.10 Possible Errors and Edge Cases
- **Confusing Correlation with Cause**: The UI distinguishes between primary bottlenecks (`STUDENT_CONFLICT`) and secondary bottlenecks (`NO_ROOMS_AVAILABLE`).

---

## Module 10 — Analytics & Reports

### 10.1 Purpose
Produces operational performance analytics, resource reconciliation audits, and exportable master timetable data feeds.

### 10.2 Problem It Solves
Provides institutional leadership with audit-ready reconciliations proving that confirmed room usage, proctor hours, and student seats match registered inputs without discrepancy.

### 10.3 Who Uses It
- Institutional Research & Reporting
- Examination Operations Directors
- External Auditors & Academic Regulators

### 10.4 Data It Reads
- Operational reconciliations (`getRunReconciliation()`)
- Aggregated room and seat utilization percentages
- Proctor hours and staffing ratios
- Accommodation compliance ratios

### 10.5 Data It Creates or Modifies
Generates on-the-fly downloadable CSV timetables and structured JSON export feeds.

### 10.6 Backend API Endpoints
- `GET /api/export/runs/{id}/csv`: Full CSV timetable export.
- `GET /api/export/runs/{id}/json`: Machine-readable master timetable JSON payload.
- `GET /api/scheduling/runs/{id}/reconciliation`: Mathematical resource reconciliation summary.

### 10.7 Database Tables Involved
- `schedule_assignments`, `assignment_students`, `assignment_invigilators`, `rooms`, `invigilators`, `run_exam_students`

### 10.8 Important Buttons and Actions
- **Export Schedule (CSV)**: Downloads `schedule_run_<id>.csv` containing assignment codes, courses, rooms, proctors, and timestamps.
- **Export Master Feed (JSON)**: Downloads comprehensive JSON structure for SIS/portal integration.

### 10.9 Expected Successful Result
Renders charts for completion and resource usage, presents verified reconciliation tallies, and triggers clean file downloads.

### 10.10 Possible Errors and Edge Cases
- **Exporting Draft Run**: Exports are clearly labeled with draft/published status watermarks in the metadata headers.

---

## Module 11 — Audit & Activity

### 11.1 Purpose
Maintains a tamper-evident, append-only governance trail of all operational actions, solver runs, approvals, and administrative mutations.

### 11.2 Problem It Solves
Guarantees institutional accountability and non-repudiation. Prevents unauthorized or unrecorded schedule modifications.

### 11.3 Who Uses It
- Internal Audit & Compliance Officers
- IT Security Administrators
- Examination Ombudspersons

### 11.4 Data It Reads
- Append-only audit logs (`audit_logs`)
- State transition events (`schedule_events`)
- Actor email addresses, roles, and IP addresses

### 11.5 Data It Creates or Modifies
System-generated write-only records. PostgreSQL triggers block all `UPDATE` and `DELETE` queries at the database engine level.

### 11.6 Backend API Endpoints
- `GET /api/audit/logs`: Paginated audit log entries with action and entity filtering.
- `GET /api/audit/events`: State transition snapshots.

### 11.7 Database Tables Involved
- `audit_logs`, `schedule_events`, `user_profiles`

### 11.8 Important Buttons and Actions
- **Action Filter**: Filter by action types (`CREATE_RUN`, `EXECUTE_SOLVER`, `APPROVE_RUN`, `PUBLISH_RUN`).
- **Diff Inspection**: Opens drawer rendering formatted before-and-after JSON state snapshots.

### 11.9 Expected Successful Result
Renders chronological ledger of events showing timestamp, operator email, role, action, and JSON diffs.

### 11.10 Possible Errors and Edge Cases
- **Database Tampering Attempt**: An SQL `DELETE` or `UPDATE` on `audit_logs` raises PostgreSQL exception `P0001: Disallowed: table audit_logs is append-only`.

---

## Module 12 — Administration & Governance

### 12.1 Purpose
Governs user accounts, role-based access permissions (RBAC), configurable scheduling constraints, and institutional parameters.

### 12.2 Problem It Solves
Allows the institution to tune operational settings (e.g., student-to-proctor ratios, minimum break intervals) without code redeployment, while enforcing strict role boundaries.

### 12.3 Who Uses It
- System Administrators
- Platform Security Officers
- Academic Policy Administrators

### 12.4 Data It Reads
- User accounts and roles (`user_profiles`)
- Academic period boundaries (`academic_periods`)
- System settings and constraint configurations

### 12.5 Data It Creates or Modifies
Provisions operator accounts, updates roles, and configures scheduling rules.

### 12.6 Backend API Endpoints
- `GET /api/auth/profiles`: Lists system users and role assignments.
- `POST /api/auth/dev-switch-role`: Development perspective switcher (guarded in production).

### 12.7 Database Tables Involved
- `user_profiles`, `academic_periods`

### 12.8 Important Buttons and Actions
- **Tab Navigation**: Switch between "User Accounts & RBAC", "Scheduling Rules & Constraints", and "Institutional Configuration".
- **Assume Role**: Allows testing the UI from different institutional perspectives (e.g., Learner vs Academic Administrator).

### 12.9 Expected Successful Result
Lists 45 system operator accounts, active academic period settings, and active scheduling rule parameters.

### 12.10 Possible Errors and Edge Cases
- **Learner Access**: Learners attempting to access `/admin` receive HTTP 403 Forbidden with clear permission guidance.
- **Production Switcher Lockdown**: Role switcher is strictly disabled when `ENVIRONMENT=production`.

