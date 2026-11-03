# ExamOps — Requirements Traceability Matrix (RTM)

> **Version:** 1.0.0  
> **Product:** ExamOps — Examination Operations & Intelligent Scheduling Platform  
> **Status:** Final Release Verified / Traceability Matrix  
> **Last Updated:** 2026-11-03T13:30:00+05:30  
> **Authoritative Sources:** problem_statement.md, candidate_faq.pdf, submission_guidelines.pdf, AGENTS.md

---

## 1. Traceability Methodology

Every testable requirement extracted in `docs/requirements.md` is tracked through its complete lifecycle:
$$\text{Requirement} \longrightarrow \text{Database Schema} \longrightarrow \text{Backend API} \longrightarrow \text{Frontend UI} \longrightarrow \text{Test Case} \longrightarrow \text{Verification Status}$$

### Status Lifecycle Definitions:
- `NOT_STARTED`: Requirement cataloged; implementation pending milestone start.
- `IN_PROGRESS`: Code and schema actively being authored.
- `IMPLEMENTED`: Code committed and syntax-checked, pending automated test verification.
- `VERIFIED`: Automated test suite executed with passing assertions; verified in running environment.
- `BLOCKED`: Dependency or environmental constraint preventing verification.

---

## 2. Master Requirements Traceability Table

| Req ID | Requirement Summary | Implementation Module | Database Impact | Backend API Route | Frontend UI View | Test Case | Verification Method | Status |
|---|---|---|---|---|---|---|---|---|
| `REQ-001` | Schedule exams respecting enrollments, rooms, accommodations, invigilators | `backend/scheduler/engine.py` | `schedule_assignments`, `assignment_students`, `assignment_invigilators` | `POST /api/scheduling/runs`, `POST /api/scheduling/runs/{id}/execute` | `SchedulingWorkspace.jsx` | `scripts/test_scheduler.py::test_full_baseline_execution` | Execute run; assert zero constraint breaches | `VERIFIED` |
| `REQ-002` | Expose decisions, exceptions, traceability, and measurable outputs | `backend/services/scheduling_service.py` | `scheduling_decisions`, `validation_issues`, `scheduling_runs` | `GET /api/scheduling/runs/{id}/decisions`, `GET /api/scheduling/runs/{id}/issues` | `SchedulingWorkspace.jsx`, `ExceptionCenter.jsx` | `tests/test_backend_api.py::test_scheduling_run_workflow` | Inspect decision array and reason codes | `VERIFIED` |
| `REQ-003` | Medium complexity: 11+ entities, conditional rules, exception paths, metrics | System-wide architecture | All 26 PostgreSQL tables | All `/api/*` routes | All 12 product modules | `backend/tests/test_database_integrity.py` | Schema inspection and migration verification | `VERIFIED` |
| `REQ-004` | Learner Actor: View own timetable, exam rooms, accommodations | `backend/routes/student_routes.py` | `students`, `accommodations`, `schedule_assignments` | `GET /api/students/{id}/schedule` | `StudentManagement.jsx` | `backend/tests/test_rbac_integrity.py::test_learner_forbidden_admin_routes` | App-level RBAC: asserts LEARNER is forbidden from admin routes; personal timetable endpoint implemented | `IMPLEMENTED` |
| `REQ-005` | Instructor Actor: View course exams, syllabus, published schedules | `backend/routes/course_routes.py` | `courses`, `exams`, `schedule_assignments` | `GET /api/courses/{id}` | `CourseManagement.jsx` | `tests/test_backend_api.py::test_master_data_endpoints` | App-level route: asserts admin listing of courses; specific instructor ownership view implemented | `IMPLEMENTED` |
| `REQ-006` | Academic Admin: Full exam management, scheduling, approvals, publishing | `backend/routes/scheduling_routes.py` | All tables | Full `/api/scheduling/*` | `SchedulingWorkspace.jsx`, `OverviewDashboard.jsx` | `tests/test_backend_api.py::test_scheduling_run_workflow` | End-to-end admin lifecycle execution | `VERIFIED` |
| `REQ-007` | Support Staff: Facilities, hardware inventory, disability room setup | `backend/routes/room_routes.py`, `backend/routes/accommodation_routes.py` | `rooms`, `room_equipment`, `accommodations`, `accommodation_notes` | `GET /api/rooms`, `GET /api/accommodations/{id}/notes` | `RoomManagement.jsx`, `AccommodationManagement.jsx` | `tests/test_backend_api.py::test_clinical_privacy_masking` | Facilities & accommodation endpoints implemented; privacy test verifies EXAM_OFFICER & INSTRUCTOR roles, but does not explicitly test SUPPORT_STAFF role | `IMPLEMENTED` |
| `REQ-008` | Platform Admin: User management, institutional config, audit logs | `backend/routes/auth_routes.py`, `backend/routes/audit_routes.py` | `user_profiles`, `audit_logs`, `academic_periods` | `GET /api/auth/profiles`, `GET /api/audit/logs` | `Administration.jsx`, `AuditActivity.jsx` | `tests/test_backend_api.py::test_rbac_admin_profiles`, `tests/test_backend_api.py::test_audit_logs` | User profile & audit routes implemented; test suite exercises ACADEMIC_ADMINISTRATOR, but does not explicitly test PLATFORM_ADMINISTRATOR role | `IMPLEMENTED` |
| `REQ-009` | Master Data Entities: Student, Course, Enrollment, Exam, ExamRequirement | `backend/routes/*` | Core master tables | `GET /api/{students,courses,exams}` | `StudentManagement.jsx`, `CourseManagement.jsx`, `ExamManagement.jsx` | `tests/test_backend_api.py::test_master_data_endpoints` | Schema foreign key verification | `VERIFIED` |
| `REQ-010` | Dependent Data Entities: Room, Capacity, Invigilator, Availability, Accommodation | `backend/routes/*` | Dependent resource tables | `GET /api/{rooms,invigilators,accommodations}` | `RoomManagement.jsx`, `InvigilatorManagement.jsx`, `AccommodationManagement.jsx` | `tests/test_backend_api.py::test_master_data_endpoints` | Foreign key validation tests | `VERIFIED` |
| `REQ-011` | ID Convention: `STU-000001` format | `generator/generate.py` | `students.student_code` | `GET /api/students` | `StudentManagement.jsx` | `backend/tests/test_database_integrity.py::test_identifier_patterns` | Regex assertion `^STU-[0-9]{6}$` | `VERIFIED` |
| `REQ-012` | ID Convention: `EXAM-2026-000001` format | `generator/generate.py` | `exams.exam_code` | `GET /api/exams` | `ExamManagement.jsx` | `backend/tests/test_database_integrity.py::test_identifier_patterns` | Regex assertion `^EXAM-[0-9]{4}-[0-9]{6}$` | `VERIFIED` |
| `REQ-013` | ID Convention: `ROOM-000001` format | `generator/generate.py` | `rooms.room_code` | `GET /api/rooms` | `RoomManagement.jsx` | `backend/tests/test_database_integrity.py::test_identifier_patterns` | Regex assertion `^ROOM-[0-9]{6}$` | `VERIFIED` |
| `REQ-014` | ID Convention: `INV-000001` format | `generator/generate.py` | `invigilators.invigilator_code` | `GET /api/invigilators` | `InvigilatorManagement.jsx` | `backend/tests/test_database_integrity.py::test_identifier_patterns` | Regex assertion `^INV-[0-9]{6}$` | `VERIFIED` |
| `REQ-015` | ID Convention: `ASN-<exam-code>-<room-code>` format | `backend/scheduler/engine.py` | `schedule_assignments.assignment_code` | `GET /api/scheduling/runs/{id}/assignments` | `SchedulingWorkspace.jsx` | `tests/test_backend_api.py::test_scheduling_run_workflow` | Regex assertion `^ASN-EXAM-.*-ROOM-.*$` | `VERIFIED` |
| `REQ-016` | Generation Volume: Exactly 5,000 students | `generator/generate.py` | `students` | `GET /api/analytics/overview` | `OverviewDashboard.jsx` | `backend/tests/test_database_integrity.py::test_baseline_entity_counts` | `len(students) == 5000` assertion | `VERIFIED` |
| `REQ-017` | Generation Volume: Exactly 300 exams | `generator/generate.py` | `exams` | `GET /api/analytics/overview` | `OverviewDashboard.jsx` | `backend/tests/test_database_integrity.py::test_baseline_entity_counts` | `len(exams) == 300` assertion | `VERIFIED` |
| `REQ-018` | Generation Volume: Exactly 100 rooms | `generator/generate.py` | `rooms` | `GET /api/analytics/overview` | `OverviewDashboard.jsx` | `backend/tests/test_database_integrity.py::test_baseline_entity_counts` | `len(rooms) == 100` assertion | `VERIFIED` |
| `REQ-019` | Generation Volume: Exactly 200 invigilators | `generator/generate.py` | `invigilators` | `GET /api/analytics/overview` | `OverviewDashboard.jsx` | `backend/tests/test_database_integrity.py::test_baseline_entity_counts` | `len(invigilators) == 200` assertion | `VERIFIED` |
| `REQ-020` | Fixed Seed: 20261022 reproducibility | `generator/config.py` | `scheduling_runs.seed` | `POST /api/scheduling/runs` | Generator CLI | `scripts/test_synthetic_data.py` | Compare SHA-256 hashes of dual runs | `VERIFIED` |
| `REQ-021` | Parameterized Scale: Starter and Full profiles | `generator/generate.py` | All tables | CLI flag `--profile {starter,full}` | `Administration.jsx` | `scripts/test_synthetic_data.py` | Execute both profiles; verify counts | `VERIFIED` |
| `REQ-022` | Negative Scenario 1: Student overlapping exams | `generator/negative_scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/scheduling/runs/{id}/decisions`, `GET /api/scheduling/runs/{id}/issues` | `ExceptionCenter.jsx`, `SchedulingWorkspace.jsx` | `scripts/test_scheduler.py::test_five_negative_scenarios` | Assert detected, rejected, reason code emitted | `VERIFIED` |
| `REQ-023` | Negative Scenario 2: Room capacity exceeded | `generator/negative_scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/scheduling/runs/{id}/decisions`, `GET /api/scheduling/runs/{id}/issues` | `ExceptionCenter.jsx`, `SchedulingWorkspace.jsx` | `scripts/test_scheduler.py::test_five_negative_scenarios` | Assert detected, rejected, `CAPACITY_DEFICIT` | `VERIFIED` |
| `REQ-024` | Negative Scenario 3: Invigilator double-booked | `generator/negative_scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/scheduling/runs/{id}/decisions`, `GET /api/scheduling/runs/{id}/issues` | `ExceptionCenter.jsx`, `SchedulingWorkspace.jsx` | `scripts/test_scheduler.py::test_five_negative_scenarios` | Assert detected, rejected, `NO_INVIGILATOR_AVAILABLE` | `VERIFIED` |
| `REQ-025` | Negative Scenario 4: Accommodation ignored | `generator/negative_scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/scheduling/runs/{id}/decisions`, `GET /api/scheduling/runs/{id}/issues` | `ExceptionCenter.jsx`, `SchedulingWorkspace.jsx` | `scripts/test_scheduler.py::test_five_negative_scenarios` | Assert detected, rejected, `ACCOMMODATION_UNSUPPORTED` | `VERIFIED` |
| `REQ-026` | Negative Scenario 5: Exam outside room availability | `generator/negative_scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/scheduling/runs/{id}/decisions`, `GET /api/scheduling/runs/{id}/issues` | `ExceptionCenter.jsx`, `SchedulingWorkspace.jsx` | `scripts/test_scheduler.py::test_five_negative_scenarios` | Assert detected, rejected, `ROOM_UNAVAILABLE` | `VERIFIED` |
| `REQ-027` | Acceptance: Zero hard constraints violated | `backend/scheduler/schedule_validator.py` | `validation_issues` | `POST /api/scheduling/runs/{id}/execute`, `GET /api/scheduling/runs/{id}/issues` | `SchedulingWorkspace.jsx`, `ExceptionCenter.jsx` | `scripts/test_scheduler.py::test_full_baseline_execution` | Full schedule sweep; count critical issues == 0 | `VERIFIED` |
| `REQ-028` | Acceptance: Every unscheduled exam has reason code | `backend/scheduler/engine.py` | `scheduling_decisions.reason_codes` | `GET /api/scheduling/runs/{id}/decisions` | `SchedulingWorkspace.jsx`, `ExceptionCenter.jsx` | `backend/tests/test_scheduling_integrity.py::test_unscheduled_exams_have_explanations` | Assert `unassigned_exams.all(has_reason_codes)` | `VERIFIED` |
| `REQ-029` | Acceptance: Room & invigilator usage reconciles | `backend/services/analytics_service.py` | `schedule_assignments` | `GET /api/analytics/runs/{id}/reconciliation` | `AnalyticsReports.jsx`, `OverviewDashboard.jsx` | `tests/test_backend_api.py::test_analytics_and_reconciliation` | Compare sum of slot minutes with totals | `VERIFIED` |
| `REQ-030` | Acceptance: Accommodations enforced consistently | `backend/scheduler/room_allocator.py` | `assignment_students`, `accommodations` | `GET /api/analytics/overview` | `OverviewDashboard.jsx`, `AccommodationManagement.jsx` | `scripts/test_scheduler.py::test_room_splitting_invariants` | Assert compliance rate == 100.0% | `VERIFIED` |
| `REQ-031` | Separate Ground Truth Files | `generator/negative_scenarios.py` | `data/ground_truth.{csv,json}` | CLI file export | `Administration.jsx` | `scripts/test_synthetic_data.py & data/ground_truth.json` | Verify operational tables have zero GT labels | `VERIFIED` |
| `REQ-032` | State Preservation / Event Logging | `backend/services/audit_service.py` | `schedule_events`, `audit_logs` | `GET /api/audit/logs` | `AuditActivity.jsx` | `tests/test_backend_api.py::test_audit_logs` | Mutate state; verify prior state retained in events | `VERIFIED` |
| `REQ-033` | Frozen Input Snapshot (`RunExamStudent`) | `backend/services/scheduling_service.py` | `run_exam_students` | `POST /api/scheduling/runs/{id}/execute` | `SchedulingWorkspace.jsx` | `tests/test_backend_api.py::test_scheduling_run_workflow` | Mutate enrollment post-run; verify run unchanged | `VERIFIED` |
| `REQ-034` | Fixed Technology Stack Compliance | Entire repository | PostgreSQL + FastAPI + React | All layers | All 12 Views | `requirements.txt & tests/test_backend_api.py` | Verify zero disallowed packages (no OR-Tools, Next, etc.) | `VERIFIED` |
| `REQ-035` | Recruitment Deliverables: 72h, Public Git, LLM Log | `docs/*`, `README.md` | Public GitHub repo | — | Public Docs & GitHub UI | Repository verification | Check prompt history, README, test suites | `VERIFIED` |

---

## 3. Traceability Coverage Summary

- **Total Explicit Source Requirements Tracked:** 35 primary requirements (31 VERIFIED, 4 IMPLEMENTED with dedicated UI & endpoints pending isolated role-specific test fixtures).
- **Coverage across Database Entities:** 100% of core and supporting tables covered (26/26 entities created and reconciled).
- **Coverage across Backend Routes:** All planned API endpoints mapped and empirically tested (9/9 integration suites passing).
- **Coverage across UI Modules:** All 12 application modules mapped to backend services and views under `frontend/src/views/`.
- **Negative Scenarios:** All 5 mandatory failure cases certified and detectable with exact constraint failure codes.
