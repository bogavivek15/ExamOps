# ExamOps — Candidate Interview Defense Guide

> **Document:** Candidate Interview Defense & Architectural Deep-Dive  
> **Target Audience:** Technical Hiring Managers, Principal System Architects, Academic Operations Leads  
> **Product:** ExamOps — Examination Operations & Intelligent Scheduling Platform  
> **Author:** Antigravity Principal Engineering Agent  

---

## 1. Executive Summary & Problem Space

### What is ExamOps?
ExamOps is an end-to-end examination operations platform designed to solve the NP-complete academic timetabling problem while providing institutional governance, full decision telemetry, and strict FERPA/GDPR student privacy protections.

### What are the core challenges of examination operations?
1. **Combinatorial explosion:** With 5,000 students taking 300 examinations across 100 venues over a 14-day window, the search space for conflict-free slot, room, and invigilator assignments is astronomical ($> 10^{600}$ candidate assignments).
2. **Hard vs. Soft constraints:** In an academic institution, certain rules are non-negotiable invariants (no student can sit two exams concurrently; no room can exceed its physical desk count; no proctor can be double-booked; no accommodation can be ignored). A solver that produces "almost valid" schedules is unacceptable.
3. **The "Black Box" problem:** Traditional solvers (like OR-Tools or CP-SAT) optimize mathematical penalty functions but cannot explain *why* an exam could not be scheduled or provide actionable advice to an academic registrar.
4. **Data drift & non-repudiation:** If student enrollments change after a schedule is generated, historical scheduling runs must remain immutable. Publications must be atomic and legally traceable.

---

## 2. Technical Stack Defense: Why These Specific Choices?

| Technology | Selection | Why Selected Over Alternatives? |
|---|---|---|
| **Frontend** | React 18 + Vite + Tailwind CSS | Vite offers near-instant HMR (sub-50ms) and clean, lightweight bundling without Next.js SSR complexity. Tailwind CSS enables tokenized enterprise design with zero runtime overhead. No TypeScript was used to keep code directly inspectable in pure ES6+. |
| **Backend** | Python 3.12 + FastAPI + Pydantic | FastAPI offers asynchronous ASGI performance, native OpenAPI documentation generation, and robust schema validation via Pydantic. Python standard library structures provide complete determinism and interview explainability. |
| **Database** | Supabase PostgreSQL 16 | PostgreSQL provides robust ACID transactions, explicit row locking (`FOR UPDATE`), complex relational integrity (composite foreign keys), JSONB semi-structured storage for immutable snapshots, and Row Level Security (RLS). |
| **Scheduling Algorithm** | Pure Deterministic Python Solver | Avoided black-box linear solvers (Google OR-Tools, CP-SAT) and LLMs. A custom deterministic greedy heuristic with largest-degree-first graph coloring provides sub-second execution, reproducible outputs, and transparent failure telemetry. |
| **State Management** | Native React Hooks & Context | Redux was rejected because application state is primarily server-driven master data and localized operational drawer workflows. Native Context and custom API hooks avoid boilerplate and state sync bugs. |

---

## 3. Algorithm Architecture & Mathematical Formulation

### 3.1 Conflict Graph Formulation
Let $E = \{e_1, e_2, \dots, e_n\}$ be the set of examinations.
Let $S(e)$ denote the set of enrolled students for examination $e$.
The conflict graph $G = (V, E_G)$ is constructed as:
- $V = E$ (each vertex represents an examination)
- $(e_i, e_j) \in E_G \iff S(e_i) \cap S(e_j) \neq \emptyset$

The degree of vertex $e$, denoted $\deg(e)$, represents the number of other examinations with which $e$ shares at least one student.

### 3.2 Ordering Heuristic: Largest Degree First (LDF) + Cohort Size Tie-Breaking
Examinations are sorted in descending order of constraint difficulty:
$$\text{Priority}(e) = (\deg(e), |S(e)|, \text{duration}(e))$$
*Rationale:* Examinations that conflict with the largest number of other exams or have the largest student cohorts are the hardest to place. Scheduling them first maximizes the probability that conflict-free time slots and large venues are available.

### 3.3 Slot Selection & Heuristic Scoring
For each examination $e$, available time slots $t \in T$ are evaluated chronologically. A slot $t$ is viable if:
$$\forall e' \in \text{Scheduled}(t), \quad (e, e') \notin E_G$$
Among all viable slots, a candidate slot is scored using an objective penalty function:
$$\text{Penalty}(e, t) = w_1 \cdot \text{ConsecutiveExamPenalty}(e, t) + w_2 \cdot \text{DaySpreadPenalty}(e, t)$$
Where:
- $w_1 = 50.0$ penalizes students having back-to-back exams on the same calendar day.
- $w_2 = 20.0$ balances exam volume across the 14-day window.

### 3.4 Room Allocation & The Seven Room-Splitting Invariants
When an exam's cohort size $|S(e)|$ exceeds the capacity of any single room:
1. **Single vs. Split Decision:** If $|S(e)| \le \max_{r \in R} \text{Capacity}(r)$, the solver selects the smallest room $r$ where $\text{Capacity}(r) \ge |S(e)|$ to maximize room fill density.
2. **Multi-Room Splitting:** If $|S(e)| > \max \text{Capacity}(r)$, the cohort is partitioned across multiple simultaneous venues. The solver guarantees:
   - Same start time and end time across all split venues.
   - Sum of room capacities $\ge |S(e)|$.
   - Independent invigilators assigned to each split venue (minimum 1 proctor per 30 students per room).
   - Venues clustered in the same building and floor.
   - Deterministic student seating assignment by sorted student ID.

### 3.5 Time Complexity Analysis
- Conflict graph construction: $\mathcal{O}(|E| \cdot \text{avg}(|S|)^2)$
- Sorting: $\mathcal{O}(|E| \log |E|)$
- Slot and Room Allocation: $\mathcal{O}(|E| \cdot |T| \cdot |R|)$
- Overall Complexity: $\mathcal{O}(|E| \log |E| + |E| \cdot |T| \cdot |R|)$
For $|E| = 300$, $|T| = 42$, and $|R| = 100$, the maximum evaluations are on the order of $10^6$ operations, executing in under **0.5 seconds** in pure Python.

---

## 4. Database Engineering & Schema Integrity

### 4.1 Schema Normalization & Entity Count
The database schema consists of **26 normalized tables** organized into three distinct tiers:
1. **Master Data Tier (Core Entities):** `students`, `courses`, `enrollments`, `exams`, `exam_requirements`, `rooms`, `room_capacities`, `room_equipment`, `equipment_types`, `room_availabilities`, `invigilators`, `availabilities`, `accommodations`, `academic_periods`.
2. **Operational Scheduling Tier:** `scheduling_runs`, `run_exam_students`, `schedule_assignments`, `assignment_students`, `assignment_invigilators`, `scheduling_decisions`, `validation_issues`, `schedule_events`.
3. **Governance & Security Tier:** `user_profiles`, `user_roles`, `role_permissions`, `audit_logs`.

### 4.2 Handling Student Input Snapshots (`run_exam_students`)
*Problem:* In universities, students add/drop courses frequently. If a schedule was generated in November for December finals, an enrollment change in December must not silently corrupt the November scheduling run.  
*Solution:* At scheduling run initiation, ExamOps creates an immutable snapshot of all enrolled students for the period in `run_exam_students` with an SHA-256 integrity hash. All assignments reference this snapshot.

### 4.3 Composite Foreign Keys for Referential Integrity
To prevent cross-run or cross-exam student seating corruption, `assignment_students` enforces a composite foreign key:
```sql
CONSTRAINT fk_ast_run_exam_student 
FOREIGN KEY (scheduling_run_id, exam_id, student_id) 
REFERENCES run_exam_students (scheduling_run_id, exam_id, student_id)
```
This guarantees that a student snapshot from Run A can never be linked to an assignment in Run B.

### 4.4 Atomic Publication via Stored Procedure
Official timetable publication uses `publish_schedule_run(uuid, uuid)`:
1. Acquires an exclusive row-level lock on `academic_periods` (`FOR UPDATE`).
2. Identifies any currently published run for that period and atomically updates its status to `SUPERSEDED`.
3. Sets the target run and its associated exams to `PUBLISHED`.
4. Emits immutable records into `schedule_events` and `audit_logs`.
5. Commits atomically—preventing concurrent race conditions where two administrators publish competing schedules simultaneously.

---

## 5. Security, Privacy & Compliance Defense

### 5.1 FERPA / GDPR Medical Privacy Protections
*Requirement:* Student accommodations often arise from medical, psychological, or neurological assessments. While proctors and instructors need to know *what* accommodations a student requires (e.g. +30 minutes, wheelchair desk), they must never see the student's clinical diagnosis.  
*Implementation:* In `AccommodationService.get_accommodation_notes`, caller roles are strictly inspected. Non-administrative roles (`STUDENT`, `INSTRUCTOR`, `INVIGILATOR`) receive a masked clinical note:
`"[CONFIDENTIAL CLINICAL RECORD REDACTED - AUTHORIZED ACCESS ONLY]"`
Only authorized administrators (`ACADEMIC_ADMINISTRATOR`, `PLATFORM_ADMINISTRATOR`) receive decrypted medical evaluations.

### 5.2 Row Level Security (RLS) & Anti-Recursion
All 26 tables enable PostgreSQL Row Level Security. To prevent infinite recursion in RLS policies (where querying `user_profiles` to check a user's role triggers the policy on `user_profiles`), security helper functions (`get_auth_role()`, `is_admin()`) were marked `SECURITY DEFINER` with an explicit `SET search_path = public`.

---

## 6. How to Walk Through the Application in an Interview

### 1. The Overview Dashboard (`/`)
* **Show:** The real-time metric cards (5,000 students, 300 exams, 100 rooms, 200 invigilators).
* **Explain:** Emphasize that every metric is derived directly from live PostgreSQL database records, with zero mocked data.

### 2. The Scheduling Operations Center (`/scheduling`)
* **Show:** The Run Selector, the "Execute Schedule Solver" button, and the resulting timetable.
* **Demonstrate:** Click on an assignment to open the assignment inspector. Show the seated student count, the assigned primary proctor, and room capacity fill.
* **Highlight:** Open the **Decision Telemetry Drawer**. Point out the evaluated slots, the reasons alternatives were rejected, and the mathematical proof of constraint compliance.

### 3. The Exception Center (`/exceptions`)
* **Show:** How unscheduled examinations are categorized with exact reason codes (e.g. `STUDENT_CONFLICT`, `NO_ROOM_CAPACITY`).
* **Explain:** Show the suggested corrective actions (e.g. expanding room operating windows, allowing multi-room splitting) and explain that ExamOps does not silently alter institutional rules.

### 4. Accommodation Governance (`/accommodations`)
* **Demonstrate:** Inspect an accommodated candidate's notes as an Administrator (full physician notes visible). Then use the **Assume Role** simulator in Administration (`/admin`) to switch to a Student or Invigilator role, return to Accommodations, and show that the medical text is instantly redacted.

### 5. Audit & Activity Trail (`/audit`)
* **Show:** The append-only governance ledger recording every state change, actor, and JSON state mutation diff.

---

## 7. Key Interview Questions & Crisp Answers

**Q: How does ExamOps guarantee that no two students have overlapping exams?**  
*A: Through an independent two-layer defense. First, the solver builds an exact conflict graph where edges represent shared students; when evaluating time slots, any slot where a conflicting exam is already scheduled is rejected. Second, before any schedule can be approved, an independent ScheduleValidator scans all confirmed student seatings across all rooms and certifies zero time overlaps.*

**Q: What happens if an exam's cohort is larger than the largest room on campus?**  
*A: ExamOps activates its room-splitting heuristic. It partitions the cohort into contiguous rooms in the same building and floor, schedules them simultaneously at the exact same start and end time, assigns dedicated proctors to each room satisfying the 1:30 ratio, and deterministically allocates seats by sorted student ID.*

**Q: Why didn't you use OR-Tools or an ILP solver?**  
*A: While OR-Tools is excellent for pure cost-minimization problems, it acts as a black box. When an exam cannot be scheduled, an ILP solver simply reports INFEASIBLE without actionable diagnostic telemetry. ExamOps records every candidate slot evaluated, every constraint that failed, and exact human-readable reason codes so that academic registrars can make informed institutional adjustments.*

**Q: How does the system handle database concurrency during schedule publication?**  
*A: Publication is managed through a PostgreSQL stored procedure (`publish_schedule_run`) that acquires an exclusive row lock (`FOR UPDATE`) on the academic period. This serializes publication requests, atomically supersedes any previously active schedule, updates all exam statuses, and logs immutable audit records within a single ACID transaction boundary.*
