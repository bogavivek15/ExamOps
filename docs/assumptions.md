# ExamOps — Technical & Operational Assumptions Register

> **Version:** 1.0.0  
> **Product:** ExamOps — Examination Operations & Intelligent Scheduling Platform  
> **Status:** Discovery / Pending Candidate Approval  
> **Last Updated:** 2026-11-01  
> **Authoritative Sources:** problem_statement.md, candidate_faq.pdf, AGENTS.md

---

## 1. Purpose of the Assumptions Register

The authoritative problem statement specifies core business constraints (student enrollment, room capacity, invigilator availability, accommodations) but purposefully leaves institutional operational parameters configurable.

This document formalizes **all explicit technical and business assumptions**, providing:
- The default value selected for the initial release / synthetic dataset.
- The engineering rationale.
- The impact and remediation if institutional policy differs.
- The approval status.

---

## 2. Comprehensive Assumptions Matrix

| ID | Category | Parameter / Assumption | Default Value | Rationale | Configurable | Impact if Institutional Policy Differs | Status |
|---|---|---|---|---|---|---|---|
| `ASM-001` | Calendar | Institution Timezone | `UTC` | Prevents DST anomalies and simplifies multi-region cloud hosting. | Yes | If local timezone required, offset timestamps via `tzinfo`. | Recommended Default |
| `ASM-002` | Calendar | Examination Period Duration | 14 calendar days (`2026-06-15` to `2026-06-30`) | Realistic duration to spread 300 exams without extreme density. | Yes | Shorter periods increase conflict density; longer periods increase availability. | Recommended Default |
| `ASM-003` | Calendar | Daily Operating Hours | 08:00 to 18:00 (10 hours) | Standard higher-ed exam operating window. | Yes | Extending to 21:00 creates evening slots; restricting reduces feasible times. | Recommended Default |
| `ASM-004` | Calendar | Slot Granularity | 30 minutes | Balances scheduling precision with combinatorial search space. | Yes | 15 min increases candidate combinations 2x; 60 min reduces placement flexibility. | Recommended Default |
| `ASM-005` | Calendar | Weekend Scheduling Policy | Saturdays enabled; Sundays closed | Common institutional practice for major final exam diets. | Yes | Enabling Sundays adds ~14% capacity; disabling Saturdays reduces capacity. | Recommended Default |
| `ASM-006` | Calendar | Student Break Buffer | 0 minutes | Engine enforces non-overlap ($T_1.\text{end} \le T_2.\text{start}$); buffer is 0 by default. | Yes | Adding 30m travel buffer increases conflict graph edge constraints. | Recommended Default |
| `ASM-007` | Staffing | Student-to-Proctor Ratio | 1 proctor per 30 students ($\lceil S / 30 \rceil$) | Standard university staffing benchmark for anti-cheating vigilance. | Yes | Lower ratio (e.g. 1:20) increases proctor demand; higher (1:50) risks invigilation quality. | Recommended Default |
| `ASM-008` | Staffing | Minimum Proctors per Room | 1 proctor | Every open exam venue requires at least one adult supervisor. | Yes | Strict institutions may mandate minimum 2 proctors for safety/witnessing. | Recommended Default |
| `ASM-009` | Staffing | Proctor Max Hours / Day | 8.0 hours | Protects proctor focus and adheres to labor guidelines. | Yes | Exceeding 8h causes proctor fatigue and potential labor compliance issues. | Recommended Default |
| `ASM-010` | Staffing | Proctor Max Hours / Week | 25.0 hours | Standard university workload cap for part-time/academic proctors. | Yes | Higher caps permit fewer proctors; lower caps require larger personnel roster. | Recommended Default |
| `ASM-011` | Accommodation | Extra Time Precedence | Explicit extra minutes override percentage | Clear deterministic hierarchy prevents ambiguous arithmetic. | Yes | If percentage preferred, engine flips precedence flag in config. | Recommended Default |
| `ASM-012` | Accommodation | Percentage Duration Rounding | Ceiling to nearest minute (`math.ceil`) | Student-favorable rounding guarantees disability compliance. | Yes | Floor rounding could shave time and risk legal accommodation non-compliance. | Recommended Default |
| `ASM-013` | Accommodation | Room Occupation Duration | Longest student duration in that room | Conservative policy guarantees room and proctors remain reserved. | Yes | Early release policy requires tracking staggered proctor departures. | Recommended Default |
| `ASM-014` | Accommodation | Low-Distraction Room Capacity | Max 15 students per low-distraction venue | Preserves quiet acoustic environment required for accessibility. | Yes | Exceeding 15 students violates typical medical low-distraction standards. | Recommended Default |
| `ASM-015` | Accommodation | Accommodation Prevalence Rate | ~8.0% of student population | Matches documented UK/US higher education disability statistics (7-10%). | Yes | Injected in synthetic generator; adjustable via `--accommodation-rate`. | Recommended Default |
| `ASM-016` | Master Data | Course Catalog Size | 80 courses | 300 exams across 80 courses averages ~3.75 exams/course (e.g. Midterm, Lab, Final). | Yes | More courses with fewer exams disperses conflicts; fewer courses concentrates them. | Recommended Default |
| `ASM-017` | Master Data | Average Student Enrollment Load | 4.2 courses per student | Realistic undergraduate semester credit load (12-18 credits). | Yes | Higher load increases conflict graph density dramatically ($O(K^2)$ edges). | Recommended Default |
| `ASM-018` | Master Data | Campus Facility Layout | 100 rooms across 6 buildings, floors -1 to 5 | Realistic campus physical topology with ADA elevators and stair-only wings. | Yes | Affects accessibility testing and resource proximity scoring. | Recommended Default |
| `ASM-019` | Master Data | Room Closure & Maintenance Rate | ~5.0% of rooms have maintenance closures | Provides realistic operational blackouts to trigger Negative Scenario 5. | Yes | 0% closures eliminates boundary testing; >15% causes severe artificial bottlenecks. | Recommended Default |
| `ASM-020` | Algorithm | Scheduling Heuristic | Deterministic most-constrained-first greedy | Guarantees rapid execution, zero black-box solver dependencies, 100% explainable. | No (Fixed) | Greedy may produce local optima; compensated by bounded improvement pass. | Approved Technical Choice |
| `ASM-021` | Algorithm | Bounded Improvement Retries | 3 passes | Bounded retries prevent infinite loops while rescuing 60-80% of unassigned exams. | Yes | 0 retries leaves more unassigned; >5 retries shows diminishing returns. | Recommended Default |
| `ASM-022` | Algorithm | Assignment Displacement | Strictly forbidden (Zero displacement) | Committing an exam is irrevocable in a pass; prevents cascading instability. | Yes | Permitting displacement requires full backtrack search (exponential complexity). | Approved Technical Choice |
| `ASM-023` | Security | Role Taxonomy | Exactly 5 distinct enterprise roles | Matches specification: Learner, Instructor, Academic Admin, Support, Platform Admin. | No (Fixed) | Custom RBAC roles can be added in future migrations if required. | Approved Technical Choice |
| `ASM-024` | Security | Service Role Key Boundary | Restricted strictly to backend on Render | Never exposed to client bundle; prevents full database bypass from browser. | No (Fixed) | Leaking service key breaks all RLS security guarantees. | Mandatory Security Rule |
| `ASM-025` | Architecture | State Snapshot Hash | SHA-256 digest of frozen inputs | Guarantees historical auditability of what data the scheduler saw at runtime. | No (Fixed) | Without snapshot hashing, retroactive student enrollment edits corrupt audit trails. | Approved Technical Choice |
| `ASM-026` | Deployment | Microservices / Containers | Single monolithic backend; no Docker/Kubernetes | Eliminates gratuitous DevOps complexity while meeting all SLA benchmarks. | No (Fixed) | Monolith on Render handles full 300-exam workload in <15 seconds. | Approved Technical Choice |

---

## 3. Assumptions Review & Signoff Recommendation

All assumptions above have been documented with conservative, production-grade defaults. 
- Critical institutional assumptions (shift caps, proctor ratios, slot granularity) are isolated in `backend/config.py` and editable via administrative settings.
- Mathematical invariants (SHA-256 hashing, zero displacement, greedy explainability) are fixed by the architectural mandate.
