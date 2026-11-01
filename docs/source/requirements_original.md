# ExamOps — Original Requirements Extraction

> **Purpose**: This document extracts and organizes every requirement from the three authoritative source documents, preserving exact original wording in quotes. It serves as the single canonical reference from which the [requirements register](../requirements.md) is derived.

---

## Source 1: problem_statement.md

### 1.1 Business Context

> "Schedule exams and rooms while respecting student enrollment, room capacity, accommodations and invigilator availability."

### 1.2 Objective and Scope

> "Build a working solution for this end-to-end workflow: Schedule exams and rooms while respecting student enrollment, room capacity, accommodations and invigilator availability. The solution should expose key decisions and exceptions, preserve traceability, and produce measurable outputs. Medium complexity means multiple related entities, conditional rules, at least one exception path and meaningful evaluation metrics."

### 1.3 Primary Actors / Systems

> "Learner, instructor, academic administrator, support staff and platform administrator."

| # | Actor | Role Context |
|---|-------|-------------|
| 1 | Learner | Student taking exams |
| 2 | Instructor | Faculty member associated with courses/exams |
| 3 | Academic Administrator | Manages scheduling, policy, approvals |
| 4 | Support Staff | Operational support for exam logistics |
| 5 | Platform Administrator | System configuration and user management |

### 1.4 Business Workflow and Rules

**Rule 1 — Master Data First**:
> "Generate/reference master data first: Student, Course, Enrollment, Exam, ExamRequirement."

**Rule 2 — Dependent Records with Valid Parents**:
> "Generate dependent transaction/event records using valid parent IDs."

**Rule 3 — Business Logic Application**:
> "Apply business logic: Create student-course enrollments; generate exams and duration requirements; define rooms, capacities and equipment; define invigilator availability and accommodation constraints; build conflict graph; assign rooms/times; report unassigned exams and reason codes."

**Rule 4 — State Preservation**:
> "Persist state changes as explicit records/events where relevant; do not overwrite history."

**Rule 5 — Ground Truth from Rules**:
> "Generate outcomes and ground-truth labels from documented rules, not independent random assignment."

### 1.5 Entities and Relationships

**Core Entities**:
> "Core entities: Student, Course, Enrollment, Exam, ExamRequirement, Room, RoomCapacity, Invigilator, Availability, Accommodation, ScheduleAssignment."

| # | Entity | Category |
|---|--------|----------|
| 1 | Student | Master Data |
| 2 | Course | Master Data |
| 3 | Enrollment | Master Data (Bridge) |
| 4 | Exam | Master Data |
| 5 | ExamRequirement | Master Data (Child) |
| 6 | Room | Dependent Data |
| 7 | RoomCapacity | Dependent Data (Child) |
| 8 | Invigilator | Dependent Data |
| 9 | Availability | Dependent Data (Child) |
| 10 | Accommodation | Dependent Data |
| 11 | ScheduleAssignment | Transaction/Event |

**Relationship Rules**:
> "Define a primary key for every entity and foreign keys for every relationship. Document cardinality (1:1, 1:N, N:M), optional relationships, effective dates and lifecycle states. Use bridge tables for many-to-many relationships; retain event history for state changes; validate all joins. For deliberate anomaly cases, keep an issue_type/ground_truth label rather than silently corrupting unrelated rows."

### 1.6 ID / Nomenclature Conventions

> "Keep counters zero-padded, IDs immutable, and referenced IDs exactly consistent across files."

| Entity | Pattern | Example |
|--------|---------|---------|
| Student | `STU-NNNNNN` | `STU-000001` |
| Exam | `EXAM-YYYY-NNNNNN` | `EXAM-2026-000001` |
| Room | `ROOM-NNNNNN` | `ROOM-000001` |
| Invigilator | `INV-NNNNNN` | `INV-000001` |
| ScheduleAssignment | `ASN-<exam-id>-<room-id>` | `ASN-EXAM-2026-000001-ROOM-000001` |

### 1.7 Synthetic Data Generation Instructions

**Step 1 — Data Dictionary**:
> "Write a data dictionary for: Student, Course, Enrollment, Exam, ExamRequirement, Room, RoomCapacity, Invigilator, Availability, Accommodation, ScheduleAssignment. For each field specify type, required/optional, allowed values, units, uniqueness and validation rule."

**Step 2 — Generation Order and Domain Logic**:
> "Create parent/master tables first, then child and event tables. Apply this domain-specific generation logic: Create student-course enrollments; generate exams and duration requirements; define rooms, capacities and equipment; define invigilator availability and accommodation constraints; build conflict graph; assign rooms/times; report unassigned exams and reason codes."

**Step 3 — Deterministic Identifiers**:
> "Apply deterministic IDs and naming: STU-000001; EXAM-2026-000001; ROOM-000001; INV-000001; ASN-<exam-id>-<room-id>. Keep counters zero-padded, IDs immutable, and referenced IDs exactly consistent across files."

**Step 4 — Baseline Volume**:
> "Generate 5,000 students, 300 exams, 100 rooms and 200 invigilators. Include overlapping enrollment conflicts, room closures, special equipment and extended-duration accommodations. Use a fixed seed (e.g. 20261022) and parameterize scale so starter and full datasets use the same generator."

**Step 5 — Labelled Edge Cases**:
> "Generate valid baseline records first, then inject labelled edge cases:"
> - "Student has overlapping exams."
> - "Room capacity exceeded."
> - "Invigilator double-booked."
> - "Accommodation ignored."
> - "Exam outside room availability."

**Step 6 — Derived Values**:
> "Calculate derived values (totals, balances, scores, statuses and dates) from source records rather than generating them independently."

**Step 7 — Ground Truth**:
> "Produce a separate ground_truth.csv/json for known anomalies, expected decisions or labels; never leak it into input features."

**Step 8 — Validation**:
> "Run validation: primary-key uniqueness, foreign-key integrity, allowed enums, date ordering, arithmetic reconciliation, lifecycle transitions and duplicate checks."

**Step 9 — Deliverables**:
> "Export CSV/JSON/SQL seed data plus README, schema/data dictionary, generator command, fixed seed, source manifest and validation summary."

**Step 10 — Reproducibility**:
> "Regenerate twice with the same seed and compare row counts/checksums to demonstrate reproducibility."

### 1.8 Suggested Volume and Coverage

> "Generate 5,000 students, 300 exams, 100 rooms and 200 invigilators. Include overlapping enrollment conflicts, room closures, special equipment and extended-duration accommodations."

### 1.9 Required Edge Cases / Negative Scenarios

> 1. "Student has overlapping exams."
> 2. "Room capacity exceeded."
> 3. "Invigilator double-booked."
> 4. "Accommodation ignored."
> 5. "Exam outside room availability."

### 1.10 Validation Rules / Acceptance Criteria

> - "No hard constraint is violated."
> - "Every unscheduled item has a reason."
> - "Room and invigilator usage reconcile."
> - "Accommodations are applied consistently."

### 1.11 Evaluation Focus for Generated Data Review

> "(a) realistic distributions and meaningful variation; (b) consistent IDs and valid joins; (c) dependency/lifecycle consistency across entities; (d) correct derived values and reconciliation; (e) normal, boundary, failure and exception coverage; (f) separate ground truth; (g) fixed-seed reproducibility, documentation and lawful provenance."

| Code | Focus Area |
|------|-----------|
| (a) | Realistic distributions and meaningful variation |
| (b) | Consistent IDs and valid joins |
| (c) | Dependency/lifecycle consistency across entities |
| (d) | Correct derived values and reconciliation |
| (e) | Normal, boundary, failure and exception coverage |
| (f) | Separate ground truth |
| (g) | Fixed-seed reproducibility, documentation and lawful provenance |

### 1.12 Public Data Guidance / Lawful Use

> "External data is optional. If used, record source URL, dataset/version, retrieval date, license/terms, attribution, transformations and fields discarded. Use only data you are legally permitted to access and redistribute; do not bypass access controls or collect confidential/personal information. If licensing or suitability is unclear, use synthetic data and cite public reference data only for schema inspiration."

### 1.13 Submission Checklist

> - "Pushed your code to a **public** GitHub repository."
> - "Added a README explaining how to run it."
> - "Included any tests the problem asks for."

---

## Source 2: candidate_faq.pdf

### Q1 — 72-Hour Window

> "When does my 72-hour window start?"
> "When YottaFlex AI sends you the project. Your deadline is exactly 72 hours later, using the recorded send timestamp and its time zone."

### Q2 — Early Submission

> "Can I submit early?"
> "Yes. You may submit as soon as you are ready. Keep your public repository available and editable until the 72-hour deadline; the latest version at the deadline is evaluated."

### Q3 — Repository Link Submission

> "How do I submit my repository link?"
> "Create a new, dedicated public GitHub repository. Send the link from the same email address you used during recruitment and follow the submission instructions provided."

### Q4 — Repository Contents

> "What belongs in my repository?"
> "Include your code, prompt history, and relevant supporting artifacts in a clearly identifiable directory. There is no fixed list of documents or prescribed format."

### Q5 — AI Tools

> "Which AI tools may I use?"
> "Any LLM or AI coding tool is allowed, including cloud-based and locally hosted tools. AI use is unrestricted; your judgment, understanding, ownership, and validation matter."

### Q6 — Prompt History

> "What prompt history is required?"
> "Include all prompts submitted to every AI tool you used. AI responses are optional. If a tool cannot export prompts, keep a reasonable record and disclose the limitation."

### Q7 — Individual Work

> "Must I write all code myself?"
> "The project must be your individual work. AI and public learning resources are allowed; implementation help from other people is not. Understand the core logic, key design choices, dependencies, and limitations."

### Q8 — Technology Stack

> "Can I choose my own technology stack?"
> "Yes. Choose suitable languages, frameworks, and storage. Use only free or locally runnable services, and avoid unusually large or slow dependencies where possible."

### Q9 — Demo / Tests

> "Must I provide a live demo or automated tests?"
> "No hosted demo or automated test suite is mandatory. Provide clear setup/run instructions and demonstrate how you verified the core functionality. Document environment needs and limitations."

### Q10 — Code Reuse

> "Can I reuse existing code?"
> "Standard dependencies and small illustrative snippets are acceptable. Do not import a complete solution or existing code that performs the core project work. Follow licenses and provide attribution where required."

### Q11 — Unclear Requirements

> "What if requirements are unclear or work is incomplete?"
> "Make reasonable assumptions and explain them. Partial solutions are acceptable if you state what works, what remains incomplete, known limitations, and next steps. Explain any requirement deviations."

### Q12 — Public Repository Safety

> "What must I keep out of a public repository?"
> "Never include secrets, credentials, personal or sensitive information, or proprietary code you are not authorized to publish. Use safe sample data and local configuration; explain setup in the README."

---

## Source 3: submission_guidelines.pdf

### Header

> "Show us how you think, build, validate, and work with AI."
> "Your submission window is 72 hours. Artifact timestamps will be used to verify the window."

### Pillar 01 — Make It Run (EXECUTABLE)

> "Submit working, executable code. Include clear steps so another person can install dependencies, configure the project, run it, and verify key behavior."

### Pillar 02 — Show Your Work (PUBLIC REPOSITORY)

> "Use a public GitHub repository. Make the evolution of your work understandable through the code, meaningful commits, and supporting context."

### Pillar 03 — Use LLMs Transparently (PROMPT HISTORY REQUIRED)

> "LLM tools are allowed. Submit your prompt history and explain where AI accelerated your work, where you relied heavily on it, and what you personally reviewed, changed, or validated."

### Pillar 04 — Make Your Reasoning Visible (EXPLAIN THE WHY)

> "Help reviewers understand the problem, assumptions, key decisions, trade-offs, testing approach, limitations, and how you know the solution works."

### Closing Statement

> "BE READY TO WALK US THROUGH YOUR SOLUTION. We value sound judgment, working software, honest AI disclosure, and clear communication."

---

## Cross-Reference Summary

| Category | Source Document | Requirement Count |
|----------|----------------|-------------------|
| Business Context & Scope | problem_statement.md | 2 |
| Actors | problem_statement.md | 5 |
| Workflow Rules | problem_statement.md | 5 |
| Entities & Relationships | problem_statement.md | 13 |
| ID Conventions | problem_statement.md | 6 |
| Data Generation Steps | problem_statement.md | 10 |
| Volume Specs | problem_statement.md | 4 |
| Negative Scenarios | problem_statement.md | 5 |
| Validation/Acceptance | problem_statement.md | 4 |
| Evaluation Focus | problem_statement.md | 7 |
| Public Data Guidance | problem_statement.md | 1 |
| Submission Checklist | problem_statement.md | 3 |
| FAQ Guidance | candidate_faq.pdf | 12 |
| Submission Pillars | submission_guidelines.pdf | 4 |
| **Total Extracted** | | **~81** |
