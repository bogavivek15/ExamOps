# ExamOps — Requirements Traceability Matrix (RTM)

> **Version:** 1.0.0  
> **Product:** ExamOps — Examination Operations & Intelligent Scheduling Platform  
> **Status:** Discovery / Living Traceability Document  
> **Last Updated:** 2026-11-01  
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
| `REQ-001` | Schedule exams respecting enrollments, rooms, accommodations, invigilators | `backend/scheduler/engine.py` | `schedule_assignments`, `assignment_students`, `assignment_invigilators` | `POST /api/v1/scheduling/runs` | `SchedulingWorkspace.jsx` | `test_scheduler.py::test_full_schedule_generation` | Execute run; assert zero constraint breaches | `NOT_STARTED` |
| `REQ-002` | Expose decisions, exceptions, traceability, and measurable outputs | `backend/services/scheduling_service.py` | `scheduling_decisions`, `validation_issues`, `scheduling_runs` | `GET /api/v1/scheduling/runs/{id}/decisions` | `DecisionDrawer.jsx`, `ExceptionCenter.jsx` | `test_scheduler.py::test_decision_logging` | Inspect decision array and reason codes | `NOT_STARTED` |
| `REQ-003` | Medium complexity: 11+ entities, conditional rules, exception paths, metrics | System-wide architecture | All 24 PostgreSQL tables | All `/api/v1/*` routes | All 12 product modules | `test_relationships.py::test_schema_cardinality` | Schema inspection and migration verification | `NOT_STARTED` |
| `REQ-004` | Learner Actor: View own timetable, exam rooms, accommodations | `backend/routes/students.py` | `students`, `accommodations`, `schedule_assignments` | `GET /api/v1/me/schedule` | `StudentPortal.jsx` | `test_api.py::test_learner_sees_only_own_schedule` | RLS role-based query assertion | `NOT_STARTED` |
| `REQ-005` | Instructor Actor: View course exams, syllabus, published schedules | `backend/routes/courses.py` | `courses`, `exams`, `schedule_assignments` | `GET /api/v1/courses/{id}/exams` | `CourseManagement.jsx` | `test_api.py::test_instructor_course_scoping` | Role access test with course ownership | `NOT_STARTED` |
| `REQ-006` | Academic Admin: Full exam management, scheduling, approvals, publishing | `backend/routes/scheduling.py` | All tables | Full `/api/v1/scheduling/*` | `SchedulingWorkspace.jsx`, `OverviewDashboard.jsx` | `test_api.py::test_admin_schedule_publish_flow` | End-to-end admin lifecycle execution | `NOT_STARTED` |
| `REQ-007` | Support Staff: Facilities, hardware inventory, disability room setup | `backend/routes/rooms.py` | `rooms`, `room_equipment`, `accommodations` | `GET /api/v1/rooms`, `PATCH /api/v1/rooms/{id}` | `RoomManagement.jsx` | `test_api.py::test_support_staff_masked_accommodations` | Verify accommodation private notes masked | `NOT_STARTED` |
| `REQ-008` | Platform Admin: User management, institutional config, audit logs | `backend/routes/audit.py` | `user_profiles`, `audit_logs`, `academic_periods` | `GET /api/v1/audit`, `PATCH /api/v1/admin/config` | `Administration.jsx`, `AuditActivity.jsx` | `test_api.py::test_platform_admin_governance` | Superuser privileged action verification | `NOT_STARTED` |
| `REQ-009` | Master Data Entities: Student, Course, Enrollment, Exam, ExamRequirement | `backend/routes/*` | Core master tables | `GET/POST /api/v1/{students,courses,exams}` | Management directories | `test_relationships.py::test_master_data_integrity` | Schema foreign key verification | `NOT_STARTED` |
| `REQ-010` | Dependent Data Entities: Room, Capacity, Invigilator, Availability, Accommodation | `backend/routes/*` | Dependent resource tables | `GET/POST /api/v1/{rooms,invigilators,accommodations}` | Resource directories | `test_relationships.py::test_dependent_fk_integrity` | Foreign key validation tests | `NOT_STARTED` |
| `REQ-011` | ID Convention: `STU-000001` format | `generator/generate.py` | `students.student_code` | `GET /api/v1/students` | `DataTable.jsx` | `test_generator.py::test_student_id_format` | Regex assertion `^STU-[0-9]{6}$` | `NOT_STARTED` |
| `REQ-012` | ID Convention: `EXAM-2026-000001` format | `generator/generate.py` | `exams.exam_code` | `GET /api/v1/exams` | `DataTable.jsx` | `test_generator.py::test_exam_id_format` | Regex assertion `^EXAM-[0-9]{4}-[0-9]{6}$` | `NOT_STARTED` |
| `REQ-013` | ID Convention: `ROOM-000001` format | `generator/generate.py` | `rooms.room_code` | `GET /api/v1/rooms` | `DataTable.jsx` | `test_generator.py::test_room_id_format` | Regex assertion `^ROOM-[0-9]{6}$` | `NOT_STARTED` |
| `REQ-014` | ID Convention: `INV-000001` format | `generator/generate.py` | `invigilators.invigilator_code` | `GET /api/v1/invigilators` | `DataTable.jsx` | `test_generator.py::test_invigilator_id_format` | Regex assertion `^INV-[0-9]{6}$` | `NOT_STARTED` |
| `REQ-015` | ID Convention: `ASN-<exam-code>-<room-code>` format | `backend/scheduler/engine.py` | `schedule_assignments.assignment_code` | `GET /api/v1/scheduling/runs/{id}/assignments` | `TimetableGrid.jsx` | `test_scheduler.py::test_assignment_code_format` | Regex assertion `^ASN-EXAM-.*-ROOM-.*$` | `NOT_STARTED` |
| `REQ-016` | Generation Volume: Exactly 5,000 students | `generator/generate.py` | `students` | `GET /api/v1/analytics/overview` | `MetricDisplay.jsx` | `test_generator.py::test_baseline_student_count` | `len(students) == 5000` assertion | `NOT_STARTED` |
| `REQ-017` | Generation Volume: Exactly 300 exams | `generator/generate.py` | `exams` | `GET /api/v1/analytics/overview` | `MetricDisplay.jsx` | `test_generator.py::test_baseline_exam_count` | `len(exams) == 300` assertion | `NOT_STARTED` |
| `REQ-018` | Generation Volume: Exactly 100 rooms | `generator/generate.py` | `rooms` | `GET /api/v1/analytics/overview` | `MetricDisplay.jsx` | `test_generator.py::test_baseline_room_count` | `len(rooms) == 100` assertion | `NOT_STARTED` |
| `REQ-019` | Generation Volume: Exactly 200 invigilators | `generator/generate.py` | `invigilators` | `GET /api/v1/analytics/overview` | `MetricDisplay.jsx` | `test_generator.py::test_baseline_invigilator_count` | `len(invigilators) == 200` assertion | `NOT_STARTED` |
| `REQ-020` | Fixed Seed: 20261022 reproducibility | `generator/config.py` | `scheduling_runs.seed` | `POST /api/v1/generator/run` | Generator CLI | `test_reproducibility.py::test_dual_generation_checksums` | Compare SHA-256 hashes of dual runs | `NOT_STARTED` |
| `REQ-021` | Parameterized Scale: Starter and Full profiles | `generator/generate.py` | All tables | CLI flag `--profile {starter,full}` | Admin data tools | `test_generator.py::test_profiles_shared_code` | Execute both profiles; verify counts | `NOT_STARTED` |
| `REQ-022` | Negative Scenario 1: Student overlapping exams | `generator/scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/v1/exceptions` | `ExceptionCenter.jsx` | `test_edge_cases.py::test_negative_student_overlap` | Assert detected, rejected, reason code emitted | `NOT_STARTED` |
| `REQ-023` | Negative Scenario 2: Room capacity exceeded | `generator/scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/v1/exceptions` | `ExceptionCenter.jsx` | `test_edge_cases.py::test_negative_capacity_exceeded` | Assert detected, rejected, `NO_ROOM_CAPACITY` | `NOT_STARTED` |
| `REQ-024` | Negative Scenario 3: Invigilator double-booked | `generator/scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/v1/exceptions` | `ExceptionCenter.jsx` | `test_edge_cases.py::test_negative_invigilator_double_booking` | Assert detected, rejected, `NO_INVIGILATOR_AVAILABLE` | `NOT_STARTED` |
| `REQ-025` | Negative Scenario 4: Accommodation ignored | `generator/scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/v1/exceptions` | `ExceptionCenter.jsx` | `test_edge_cases.py::test_negative_accommodation_ignored` | Assert detected, rejected, `ACCOMMODATION_UNSUPPORTED` | `NOT_STARTED` |
| `REQ-026` | Negative Scenario 5: Exam outside room availability | `generator/scenarios.py` | Fixture dataset / `validation_issues` | `GET /api/v1/exceptions` | `ExceptionCenter.jsx` | `test_edge_cases.py::test_negative_room_unavailable` | Assert detected, rejected, `ROOM_UNAVAILABLE` | `NOT_STARTED` |
| `REQ-027` | Acceptance: Zero hard constraints violated | `backend/validation/schedule_validation.py` | `validation_issues` | `POST /api/v1/scheduling/runs/{id}/validate` | `ValidationSummaryModal.jsx` | `test_constraints.py::test_zero_confirmed_violations` | Full schedule sweep; count critical issues == 0 | `NOT_STARTED` |
| `REQ-028` | Acceptance: Every unscheduled exam has reason code | `backend/scheduler/engine.py` | `scheduling_decisions.reason_codes` | `GET /api/v1/scheduling/runs/{id}` | `UnassignedExamsPanel.jsx` | `test_scheduler.py::test_unscheduled_exams_have_reasons` | Assert `unassigned_exams.all(has_reason_codes)` | `NOT_STARTED` |
| `REQ-029` | Acceptance: Room & invigilator usage reconciles | `backend/services/report_service.py` | `schedule_assignments` | `GET /api/v1/analytics/utilization` | `UtilizationCharts.jsx` | `test_scheduler.py::test_resource_reconciliation` | Compare sum of slot minutes with totals | `NOT_STARTED` |
| `REQ-030` | Acceptance: Accommodations enforced consistently | `backend/validation/schedule_validation.py` | `assignment_students`, `accommodations` | `GET /api/v1/analytics/overview` | `MetricDisplay.jsx` | `test_constraints.py::test_accommodations_compliance` | Assert compliance rate == 100.0% | `NOT_STARTED` |
| `REQ-031` | Separate Ground Truth Files | `generator/scenarios.py` | `data/ground_truth/ground_truth.{csv,json}` | CLI file export | File inspection | `test_generator.py::test_ground_truth_isolation` | Verify operational tables have zero GT labels | `NOT_STARTED` |
| `REQ-032` | State Preservation / Event Logging | `backend/services/scheduling_service.py` | `schedule_events`, `audit_logs` | `GET /api/v1/audit` | `AuditActivity.jsx` | `test_relationships.py::test_historical_state_preservation` | Mutate state; verify prior state retained in events | `NOT_STARTED` |
| `REQ-033` | Frozen Input Snapshot (`RunExamStudent`) | `backend/scheduler/engine.py` | `run_exam_students` | `POST /api/v1/scheduling/runs` | `RunDetails.jsx` | `test_scheduler.py::test_frozen_enrollment_snapshot` | Mutate enrollment post-run; verify run unchanged | `NOT_STARTED` |
| `REQ-034` | Fixed Technology Stack Compliance | Entire repository | PostgreSQL + FastAPI + React | All layers | Entire UI | Codebase audit | Verify zero disallowed packages (no OR-Tools, Next, etc.) | `NOT_STARTED` |
| `REQ-035` | Recruitment Deliverables: 72h, Public Git, LLM Log | `docs/*`, `README.md` | Public GitHub repo | — | GitHub UI | Repository verification | Check prompt history, README, test suites | `NOT_STARTED` |

---

## 3. Traceability Coverage Summary

- **Total Explicit Source Requirements Tracked:** 35 primary requirements.
- **Coverage across Database Entities:** 100% of core and supporting tables covered.
- **Coverage across Backend Routes:** All planned API endpoints mapped.
- **Coverage across UI Modules:** All 12 application modules accounted for.
- **Negative Scenarios:** All 5 mandatory failure cases explicitly linked to dedicated tests.
