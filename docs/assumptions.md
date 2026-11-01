# ExamOps — Technical & Operational Assumptions Register

> **Version:** 1.1.0  
> **Product:** ExamOps — Examination Operations & Intelligent Scheduling Platform  
> **Status:** Architecture Review / Pending Candidate Approval  
> **Last Updated:** 2026-11-01  
> **Authoritative Sources:** problem_statement.md, candidate_faq.pdf, submission_guidelines.pdf, AGENTS.md

---

## 1. Purpose & Governance of Assumptions

The authoritative problem statement specifies core business constraints (student enrollment, room capacity, invigilator availability, accommodations) but purposefully leaves institutional operational parameters configurable.

This document formalizes **all 26 explicit technical, operational, and architectural assumptions**:
1. **Explicit Source Requirements vs. Institutional Policy:** Mandatory source requirements (zero hard-constraint violations, reason codes, ground-truth separation) are strictly separated from configurable institutional policies (shift caps, invigilator ratios, slot granularity).
2. **No Unverified Legal or Standard Claims:** Configurable assumptions are explicitly identified as **configurable demonstration defaults** rather than universal industry standards or statutory mandates.
3. **Auditability & Traceability:** Every assumption is cataloged with its rationale, configurability status, architectural impact, and default value.

---

## 2. Comprehensive Assumptions Matrix (All 26 Assumptions)

| ID | Category | Parameter / Assumption | Configurable Demonstration Default | Rationale | Configurable | Impact if Institutional Policy Differs | Classification |
|---|---|---|---|---|---|---|---|
| `ASM-001` | Calendar | Institutional Scheduling Timezone | `Asia/Kolkata` (IST, UTC+05:30) | Aligns scheduling operations with the demonstration institution's operational day. All database timestamps stored in UTC; conversions to `Asia/Kolkata` occur for calendar days, operating hours, and availability. | Yes | If another timezone is designated, the engine applies the configured IANA timezone identifier via Python `zoneinfo`. | Configurable Demonstration Default |
| `ASM-002` | Calendar | Examination Period Duration | 14 inclusive calendar days (`2026-12-01` to `2026-12-14`) | Future synthetic examination window after November 1, 2026. Inclusive days calculated as $(\text{end} - \text{start} + 1) = (14 - 1 + 1) = 14$ calendar days (12 active exam days excluding Sundays). Engine does not hardcode dates. | Yes | Longer periods disperse conflicts across more slots; shorter periods concentrate resource bottlenecks. | Configurable Demonstration Default |
| `ASM-003` | Calendar | Daily Operating Hours | 08:00 to 18:00 local time (10 hours/day) | Provides a continuous 10-hour daily operational window for scheduling evaluations. | Yes | Extending to evening hours (e.g. 21:00) expands placement capacity; restricting to half-days reduces feasible slots. | Configurable Demonstration Default |
| `ASM-004` | Calendar | Time Slot Granularity | 30 minutes | Balances placement flexibility with combinatorial candidate search space. | Yes | 15-minute granularity doubles candidate search steps; 60-minute reduces room packing density. | Configurable Demonstration Default |
| `ASM-005` | Calendar | Weekend Scheduling Policy | Saturdays enabled; Sundays closed | Provides realistic weekend operational profile for intensive examination sessions. | Yes | Enabling Sundays provides ~16% additional time capacity; closing Saturdays reduces scheduling window to 10 days. | Configurable Demonstration Default |
| `ASM-006` | Calendar | Student Break Buffer | 0 minutes | Engine enforces strict non-overlap ($T_1.\text{end} \le T_2.\text{start}$). Back-to-back exams are permitted unless an institutional rest buffer is configured. | Yes | Introducing an institutional buffer (e.g. 30 or 60 min) adds temporal spacing constraints between consecutive student exams. | Configurable Demonstration Default |
| `ASM-007` | Staffing | Student-to-Invigilator Ratio | 1 invigilator per 30 students ($\lceil S / 30 \rceil$) | Demonstration staffing heuristic ensuring adequate visual supervision in examination rooms. | Yes | A tighter ratio (e.g. 1:20) increases invigilator demand; a looser ratio (e.g. 1:50) lowers personnel requirements. | Configurable Demonstration Default |
| `ASM-008` | Staffing | Minimum Invigilators per Room | 1 invigilator | Baseline requirement that no examination venue operates unattended. | Yes | Institutions requiring dual-invigilator supervision can set parameter to 2. | Configurable Demonstration Default |
| `ASM-009` | Staffing | Daily Invigilator Shift Cap | 8.0 hours per calendar day | Operational fatigue cap preventing excessive continuous proctoring duty. | Yes | Cap can be adjusted to match specific institutional workload agreements (e.g. 6.0h or 10.0h). | Configurable Demonstration Default |
| `ASM-010` | Staffing | Weekly Invigilator Workload Cap | 25.0 hours per 7-day period | Workload management parameter for academic and auxiliary invigilation staff. | Yes | Higher caps permit fewer staff to cover the schedule; lower caps require a broader invigilator pool. | Configurable Demonstration Default |
| `ASM-011` | Accommodation | Extra Time Precedence | Explicit extra minutes override percentage | Deterministic precedence hierarchy eliminates ambiguity when both absolute minutes and percentage extensions are present. | Yes | Engine configuration flag can invert precedence if institutional policy prioritizes percentage. | Configurable Demonstration Default |
| `ASM-012` | Accommodation | Percentage Duration Rounding | Ceiling to nearest integer minute (`math.ceil`) | Student-favorable rounding guarantees that calculated extra time is never truncated below approved accommodation. | Yes | Round-half-up or floor rounding could be configured if institutional policy mandates. | Configurable Demonstration Default |
| `ASM-013` | Accommodation | Room Occupation Duration | Maximum student duration in that room | Conservative operational reservation ensuring rooms and invigilators remain assigned until the last accommodated student finishes. | Yes | Early release policy would require staggered invigilator departure tracking. | Configurable Demonstration Default |
| `ASM-014` | Accommodation | Low-Distraction Room Capacity | Maximum 15 students per low-distraction venue | Acoustic and spatial threshold established for quiet examination rooms. | Yes | Institutions with smaller quiet rooms can set cap to 10 or 8. | Configurable Demonstration Default |
| `ASM-015` | Accommodation | Accommodation Prevalence Rate | ~8.0% of student population | Synthetic demographic distribution rate generating diverse accommodation profiles for testing. | Yes | Generator CLI parameter `--accommodation-rate` adjusts synthetic population percentage. | Configurable Demonstration Default |
| `ASM-016` | Master Data | Course Catalog Size | 80 academic courses | Yields an average of ~3.75 exams per course across 300 total examinations (e.g. Midterm, Lab, Final). | Yes | Adjustable in synthetic generator configuration. | Configurable Demonstration Default |
| `ASM-017` | Master Data | Average Student Enrollment Load | 4.2 courses per student | Realistic collegiate term enrollment load creating a dense, non-trivial conflict graph. | Yes | Generator configuration allows adjusting mean and standard deviation of course enrollments. | Configurable Demonstration Default |
| `ASM-018` | Master Data | Campus Physical Topology | 100 rooms across 6 buildings, floors -1 to 5 | Realistic campus layout incorporating accessibility variations (elevators, stair-only wings). | Yes | Configurable facility distribution in synthetic generator. | Configurable Demonstration Default |
| `ASM-019` | Master Data | Facility Maintenance Closure Rate | ~5.0% of rooms have scheduled closures | Generates realistic operational blackouts to trigger and verify Negative Scenario 5. | Yes | Closure rate adjustable via generator parameters (0% to 20%). | Configurable Demonstration Default |
| `ASM-020` | Algorithm | Scheduling Heuristic Strategy | Deterministic most-constrained-first greedy with candidate scoring | Guarantees rapid execution, zero unexplainable solver dependencies, and full step-by-step decision auditing. Produces a valid assignment with zero hard-constraint violations; does not claim global mathematical optimality. | No (Mandated) | Greedy assignment is heuristic; supplemented by bounded improvement pass to resolve unassigned exams. | Mandated Architectural Decision |
| `ASM-021` | Algorithm | Bounded Improvement Passes | Exactly 3 improvement passes | Bounded retries prevent combinatorial explosion or non-terminating loops while attempting to place remaining unassigned exams. | Yes | Passes can be configured from 1 to 5 depending on available compute budget. | Configurable Demonstration Default |
| `ASM-022` | Algorithm | Assignment Displacement Policy | Strictly forbidden (Zero displacement) | Committing an assignment is irrevocable within a run pass; prevents cascading instability and unbounded churn. | Yes | Permitting displacement would require full backtracking search with exponential worst-case runtime. | Mandated Architectural Decision |
| `ASM-023` | Security | Role Taxonomy | Exactly 5 distinct enterprise roles | Matches specification: Learner, Instructor, Academic Admin, Support Staff, Platform Admin. | No (Mandated) | Core enterprise RBAC structure defined in PostgreSQL enum and FastAPI security guards. | Mandated Architectural Decision |
| `ASM-024` | Security | Service Role Key Boundary | Restricted strictly to backend on Render | Never transmitted to or bundled inside the client SPA; prevents client-side bypass of database access controls. | No (Mandated) | Exposing service key to frontend violates core security contract and invalidates RLS. | Mandatory Security Mandate |
| `ASM-025` | Architecture | Input State Snapshot Hashing | SHA-256 digest of frozen input state | Guarantees historical auditability of the exact data the scheduling engine evaluated at execution time. | No (Mandated) | Without snapshot hashing, retroactive student enrollment edits corrupt audit trails and reproducibility. | Mandated Architectural Decision |
| `ASM-026` | Deployment | Monolithic Backend Topology | Single modular FastAPI backend without microservices | Eliminates gratuitous distributed systems overhead while meeting all operational requirements. Single backend executes greedy heuristic without network serialization bottlenecks; runtime performance is benchmarked empirically against scale profiles. | Mandated Architectural Decision |

---

## 3. Summary of Governance Categories

1. **Configurable Demonstration Defaults (`ASM-001` to `ASM-019`, `ASM-021`):**
   - Editable via `backend/config.py` and administrative system settings.
   - Initialized with sensible defaults for synthetic demonstrations.
   - Evaluated dynamically at runtime; never hardcoded into algorithm routines.
2. **Mandated Architectural & Security Decisions (`ASM-020`, `ASM-022` to `ASM-026`):**
   - Fixed by project mandate and engineering contracts.
   - Enforce explainability, reproducible state hashing, zero displacement, and strict key isolation.
