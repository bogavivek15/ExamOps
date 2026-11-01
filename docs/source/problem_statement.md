# YottaFlex AI Candidate Project — Problem Statement

## Business Context / Problem

Schedule exams and rooms while respecting student enrollment, room capacity, accommodations and invigilator availability.

## Objective and Scope

Build a working solution for this end-to-end workflow: Schedule exams and rooms while respecting student enrollment, room capacity, accommodations and invigilator availability. The solution should expose key decisions and exceptions, preserve traceability, and produce measurable outputs. Medium complexity means multiple related entities, conditional rules, at least one exception path and meaningful evaluation metrics.

## Primary Actors / Systems

Learner, instructor, academic administrator, support staff and platform administrator.

## Business Workflow and Rules

1. Generate/reference master data first: Student, Course, Enrollment, Exam, ExamRequirement.
2. Generate dependent transaction/event records using valid parent IDs.
3. Apply business logic: Create student-course enrollments; generate exams and duration requirements; define rooms, capacities and equipment; define invigilator availability and accommodation constraints; build conflict graph; assign rooms/times; report unassigned exams and reason codes.
4. Persist state changes as explicit records/events where relevant; do not overwrite history.
5. Generate outcomes and ground-truth labels from documented rules, not independent random assignment.

## Entities and Relationships

Core entities: Student, Course, Enrollment, Exam, ExamRequirement, Room, RoomCapacity, Invigilator, Availability, Accommodation, ScheduleAssignment.

Define a primary key for every entity and foreign keys for every relationship. Document cardinality (1:1, 1:N, N:M), optional relationships, effective dates and lifecycle states. Use bridge tables for many-to-many relationships; retain event history for state changes; validate all joins. For deliberate anomaly cases, keep an issue_type/ground_truth label rather than silently corrupting unrelated rows.

## ID / Nomenclature Conventions

- `STU-000001`
- `EXAM-2026-000001`
- `ROOM-000001`
- `INV-000001`
- `ASN-<exam-id>-<room-id>`

Keep counters zero-padded, IDs immutable, and referenced IDs exactly consistent across files.

## Synthetic Data Generation Instructions (Granular)

### Step 1 — Data dictionary

Write a data dictionary for: Student, Course, Enrollment, Exam, ExamRequirement, Room, RoomCapacity, Invigilator, Availability, Accommodation, ScheduleAssignment. For each field specify type, required/optional, allowed values, units, uniqueness and validation rule.

### Step 2 — Generation order and domain logic

Create parent/master tables first, then child and event tables. Apply this domain-specific generation logic: Create student-course enrollments; generate exams and duration requirements; define rooms, capacities and equipment; define invigilator availability and accommodation constraints; build conflict graph; assign rooms/times; report unassigned exams and reason codes.

### Step 3 — Deterministic identifiers

Apply deterministic IDs and naming: STU-000001; EXAM-2026-000001; ROOM-000001; INV-000001; ASN-<exam-id>-<room-id>. Keep counters zero-padded, IDs immutable, and referenced IDs exactly consistent across files.

### Step 4 — Baseline volume

Generate 5,000 students, 300 exams, 100 rooms and 200 invigilators. Include overlapping enrollment conflicts, room closures, special equipment and extended-duration accommodations. Use a fixed seed (e.g. 20261022) and parameterize scale so starter and full datasets use the same generator.

### Step 5 — Labelled edge cases

Generate valid baseline records first, then inject labelled edge cases:
- Student has overlapping exams.
- Room capacity exceeded.
- Invigilator double-booked.
- Accommodation ignored.
- Exam outside room availability.

### Step 6 — Derived values

Calculate derived values (totals, balances, scores, statuses and dates) from source records rather than generating them independently.

### Step 7 — Ground truth

Produce a separate ground_truth.csv/json for known anomalies, expected decisions or labels; never leak it into input features.

### Step 8 — Validation

Run validation: primary-key uniqueness, foreign-key integrity, allowed enums, date ordering, arithmetic reconciliation, lifecycle transitions and duplicate checks.

### Step 9 — Deliverables

Export CSV/JSON/SQL seed data plus README, schema/data dictionary, generator command, fixed seed, source manifest and validation summary.

### Step 10 — Reproducibility

Regenerate twice with the same seed and compare row counts/checksums to demonstrate reproducibility.

## Suggested Volume and Coverage

Generate 5,000 students, 300 exams, 100 rooms and 200 invigilators. Include overlapping enrollment conflicts, room closures, special equipment and extended-duration accommodations.

## Required Edge Cases / Negative Scenarios

1. Student has overlapping exams.
2. Room capacity exceeded.
3. Invigilator double-booked.
4. Accommodation ignored.
5. Exam outside room availability.

## Validation Rules / Acceptance Criteria

- No hard constraint is violated.
- Every unscheduled item has a reason.
- Room and invigilator usage reconcile.
- Accommodations are applied consistently.

## Evaluation Focus for Generated Data Review

(a) realistic distributions and meaningful variation; (b) consistent IDs and valid joins; (c) dependency/lifecycle consistency across entities; (d) correct derived values and reconciliation; (e) normal, boundary, failure and exception coverage; (f) separate ground truth; (g) fixed-seed reproducibility, documentation and lawful provenance.

## Public Data Guidance / Lawful Use

External data is optional. If used, record source URL, dataset/version, retrieval date, license/terms, attribution, transformations and fields discarded. Use only data you are legally permitted to access and redistribute; do not bypass access controls or collect confidential/personal information. If licensing or suitability is unclear, use synthetic data and cite public reference data only for schema inspiration.

## Submission checklist

Before submission, make sure you have:

- Pushed your code to a **public** GitHub repository.
- Added a README explaining how to run it.
- Included any tests the problem asks for.

## Source materials

The accompanying `candidate_faq.pdf` and `submission_guidelines.pdf` are the original recruitment documents supplied with the assignment.
