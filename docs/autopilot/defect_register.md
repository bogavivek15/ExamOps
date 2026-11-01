# ExamOps Autopilot — Defect Register

> **Document**: Autopilot Defect Tracking and Resolution Register  
> **System**: ExamOps Autonomous Engineering Engine  
> **Last Updated**: 2026-11-01T18:03:00+05:30  

---

## Defect Inventory

| Defect ID | Severity | Phase | Requirement / Area | Root Cause | Affected Files | Corrective Action | Test / Verification | Status |
|---|---|---|---|---|---|---|---|---|
| `DEF-001` | **HIGH** | Phase 0 | Entity Count Consistency | `docs/permissions.md` had 24 entity rows (omitted `course_instructors` and `accommodation_notes`); `docs/implementation_plan.md` and `docs/requirements_traceability.md` referenced "24 entities" while ERD & Data Dictionary define 26 entities. | `docs/permissions.md`, `docs/implementation_plan.md`, `docs/requirements_traceability.md`, `docs/ai_prompt_history.md` | Add `course_instructors` and `accommodation_notes` to permission matrix; update entity counts to 26 across all docs. | `python scripts/verify_phase0.py` passed with 26/26 match. | **RESOLVED** |
| `DEF-002` | **CRITICAL** | Phase 0 | Migration Dependency Ordering | `course_instructors` references `user_profiles.id` and `scheduling_runs` references `user_profiles.id`, but `user_profiles` was planned in migration 003 after migration 001 and 002. | `docs/implementation_plan.md`, `docs/architecture.md`, `supabase/migrations/*` plan | Reordered schema topological sort so `user_profiles` is created in core master migration before tables referencing it. | Migration plan check & topological dependency audit. | **RESOLVED** |
| `DEF-003` | **CRITICAL** | Phase 0 | Snapshot & Seating Relational Integrity | `assignment_students` FK to `schedule_assignments` and `run_exam_students` using only simple single-column IDs allows potential run/exam mismatch between assignment and snapshot. | `docs/erd.md`, `docs/data_dictionary.md`, `supabase/migrations/*` | Add composite unique keys and composite foreign keys linking `(assignment_id, scheduling_run_id, exam_id, room_id)` and `(run_exam_student_id, scheduling_run_id, exam_id, student_id)`. | Schema constraint validation in ERD & data dictionary. | **RESOLVED** |
| `DEF-004` | **HIGH** | Phase 0 | RLS Recursive Policy Evaluation | `user_profiles` RLS policy used subquery `SELECT role FROM user_profiles WHERE id = auth.uid()`, causing recursive self-lookup loop in PostgreSQL RLS. | `docs/security.md`, migration RLS | Introduce `SECURITY DEFINER` helper functions (`get_auth_role()`, `get_auth_student_id()`, `get_auth_invigilator_id()`) and column update protection trigger. | RLS policy inspection and recursion analysis. | **RESOLVED** |
| `DEF-005` | **MEDIUM** | Phase 0 | Terminology Inconsistency | Stray references to "Proctor" in `docs/erd.md`, `docs/data_dictionary.md`, `docs/testing.md`, and `docs/ui_ux_specification.md` violate AGENTS.md mandate to use "Invigilator" exclusively. | `docs/erd.md`, `docs/data_dictionary.md`, `docs/testing.md`, `docs/ui_ux_specification.md` | Replaced all "Proctor" terminology with "Invigilator". | Global regex audit confirmed ZERO proctor references in active docs. | **RESOLVED** |
