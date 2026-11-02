# ExamOps Database Test Results & Verification Log

**Date of Execution**: 2026-11-02  
**Test Framework**: Pytest 9.2.0 (Python 3.12.10)  
**Database**: Supabase Hosted PostgreSQL 17.11  
**Project Reference**: `ndlysanfeowexvtlvhxd`  

---

## 1. Test Execution Summary

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\USER\OneDrive\Desktop\ExamOps
plugins: anyio-4.16.0
collected 17 items

backend\tests\test_database_integrity.py ....                            [ 23%]
backend\tests\test_duplicate_detection.py ..                             [ 35%]
backend\tests\test_rbac_integrity.py ...                                 [ 52%]
backend\tests\test_referential_integrity.py ...                          [ 70%]
backend\tests\test_scheduling_integrity.py .....                         [100%]

======================= 17 passed, 3 warnings in 46.08s =======================
```

---

## 2. Test Suite Breakdown

### 2.1 `backend/tests/test_database_integrity.py`
- `test_baseline_entity_counts`: **PASSED** (Validated 5,000 students, 150 courses, 25,044 enrollments, 300 exams, 100 rooms, 200 invigilators, 301 accommodations).
- `test_identifier_patterns`: **PASSED** (Validated zero regex format deviations across STU, CRS, ENR, EXAM, REQ, ROOM, CAP, INV, AVL, ACO codes).
- `test_mandatory_columns_not_null`: **PASSED** (Verified zero NULL or whitespace-only records across essential student, course, room, and invigilator fields).
- `test_immutability_triggers`: **PASSED** (Verified PostgreSQL triggers reject UPDATE/DELETE queries on append-only `audit_logs` and `scheduling_decisions`).

### 2.2 `backend/tests/test_duplicate_detection.py`
- `test_unique_business_codes`: **PASSED** (Zero duplicate primary business identifiers across 11 entity types).
- `test_unique_composite_relationships`: **PASSED** (Zero duplicate student enrollments per period, zero duplicate decisions per exam/run, zero duplicate assignment codes).

### 2.3 `backend/tests/test_rbac_integrity.py`
- `test_unauthenticated_rejected`: **PASSED** (Protected endpoints reject requests without authorization token with HTTP 401).
- `test_learner_forbidden_admin_routes`: **PASSED** (Learner role is blocked with HTTP 403 when attempting administrative operations).
- `test_clinical_notes_redacted_for_instructors`: **PASSED** (FERPA/clinical medical notes are masked as `[CONFIDENTIAL MEDICAL DATA - REDACTED]` for instructors and visible only to academic administrators).

### 2.4 `backend/tests/test_referential_integrity.py`
- `test_foreign_key_referential_integrity`: **PASSED** (45 foreign key relationships audited; 0 orphaned child records found).
- `test_composite_foreign_key_integrity`: **PASSED** (Verified `assignment_students` strictly matches `schedule_assignments` on run, exam, and room).
- `test_scheduling_run_totals_consistency`: **PASSED** (Verified `total_exams == scheduled_count + unassigned_count` across completed runs).

### 2.5 `backend/tests/test_scheduling_integrity.py`
- `test_no_student_conflicts`: **PASSED** (Zero overlapping examination intervals for any student in confirmed assignments).
- `test_no_room_double_booking`: **PASSED** (Zero overlapping examination allocations in any room).
- `test_room_capacity_not_exceeded`: **PASSED** (Number of seated students in every room strictly $\le$ room examination capacity on examination date).
- `test_no_invigilator_double_booking`: **PASSED** (Zero overlapping proctor assignments).
- `test_unscheduled_exams_have_explanations`: **PASSED** (100% of unassigned examinations have documented reason codes).

---

## 3. General Backend API Test Suite (`tests/test_backend_api.py`)

```
============================= test session starts =============================
collected 9 items

tests\test_backend_api.py .........                                      [100%]
======================= 9 passed, 3 warnings in 176.28s =======================
```
- Full FastAPI endpoint lifecycle verified: Health, Auth Me, RBAC Profiles, Master Data CRUD, Privacy Redaction, End-to-End Scheduling Solver Execution, Allocation Telemetry, Approval, Publication, and Analytics Reconciliation.

