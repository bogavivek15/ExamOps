# ExamOps Frontend Language Audit

**Version:** 1.0.0  
**Date:** November 2026  
**Auditor:** Senior Frontend Engineer & UI/UX Product Designer  
**Scope:** Complete inspection across all 12 operational product modules and shared layout components.

---

## 1. Executive Summary

ExamOps was engineered with a robust relational data model and mathematical scheduling engine. However, the initial user interface presented internal engine vocabulary, database terminology, and technical jargon directly to end users. 

College administrators, department heads, and exam coordinators should not need engineering or database expertise to schedule and monitor campus examinations.

This audit catalogues confusing and overly technical phrases across every component and view, explains why each is problematic for non-technical institutional users, and provides approved, clear, professional English replacements.

---

## 2. Global Vocabulary Replacement Reference

| Category | Existing Technical Wording | Recommended Simple English | Context / Rationale |
|---|---|---|---|
| Engine & Solver | Execute Scheduling Algorithm / Solver | Create Timetable / Run Auto-Scheduler | "Solver" is mathematical jargon; coordinators create timetables. |
| Engine & Solver | Algorithmic Decision Telemetry | Scheduling Decision Details | Administrators need to know *why* an exam was scheduled, not "telemetry". |
| Engine & Solver | Deterministic Constraint Satisfaction | Automated Conflict Check | Clear explanation that rules are enforced automatically. |
| Engine & Solver | Feasibility Yield / Completion Yield | Scheduling Success Rate | Administrators evaluate percentage of exams successfully scheduled. |
| Data & Records | Data Ingestion / Synced Snapshot Locked | Import Data / Course List Confirmed | Simple, clear operational status. |
| Data & Records | Referential Integrity Violation | Linked Record Missing | Plain language explaining missing parent/child links. |
| Constraints | Hard Constraint Breach / Invariant Violation | Scheduling Rule Not Met | Institutional staff understand "rules" rather than mathematical "invariants". |
| Constraints | Student Conflict Prohibition | No Overlapping Exams | Immediately understandable to students and faculty. |
| Constraints | Venue Capacity Strict Bound | Never Exceed Room Capacity | Clear rule statement. |
| Constraints | Invigilator Non-Overlapping Bound | No Invigilator Double-Booking | Standard academic operations phrasing. |
| Roles & Auth | Authorization Rejection (HTTP 403) | Action Not Allowed | Removes HTTP error codes; clearly explains required permission. |
| Roles & Auth | Simulate Perspective / Assume Role | Switch Role Preview | Clear demonstration that the user is previewing another persona. |
| Auditing | Immutable State Mutation Payload | Recorded Changes & Details | Clear description of logged field modifications. |
| Auditing | Non-Repudiation Assurance | Tamper-Proof Audit Record | Explains that history cannot be edited without legalistic jargon. |
| Accommodations | Privacy-Shielded Clinical Records | Confidential Support Notes | Protects student dignity while remaining clear. |

---

## 3. Module-by-Module Language Audit

### Module 1: Overview Dashboard (`src/views/OverviewDashboard.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Top Header | Operational Period / Active Semester | Technical bureaucratic phrasing. | Academic Term / Current Semester | No |
| Primary CTA | Launch Scheduling Workspace | Sounds like launching a missile or complex server. | Open Scheduling Workspace | No |
| Metric 2 | Total Courses / Active catalog | "Catalog" is generic. | Total Courses / Active this term | No |
| Metric 4 | Rooms & Venues / Available spaces | Redundant wording. | Exam Rooms / Available for exams | No |
| Schedule Card | Current Operational Schedule State / Authoritative schedule output | Complex phrasing. | Current Timetable Status / Official timetable for this term | No |
| Schedule Card | Completion Rate / Feasibility yield | "Feasibility yield" is mathematical solver terminology. | Scheduling Success / Exams scheduled | No |
| Schedule Card | Seated Registrations / Students placed | Technical database concept. | Seated Students / Assigned to exam desks | No |
| Metadata Line | Run ID: ... Seed: ... Engine: v... | Raw debugging parameters cluttering primary view. | Timetable Code: ... • Version: ... (details in tooltip) | No |
| Guarantee | Zero Hard Constraint Breaches Certified / Verified by independent constraint validator | Overly mechanical wording. | All Scheduling Rules Met / Zero student clashes or room overruns | No |
| Quick Actions | Operational Actions | Stiff enterprise jargon. | Quick Actions | No |
| Quick Action 2 | Exception Center / Investigate {N} unscheduled exams | "Investigate" sounds disciplinary. | Issue Center / Review {N} unscheduled exams | No |

---

### Module 2: Scheduling Operations Center (`src/views/SchedulingWorkspace.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Toolbar | Run: | Developer shorthand. | Timetable Version: | No |
| Primary Button | Execute Solver | Technical computational phrasing. | Create Timetable | No |
| Status Message | Executing deterministic scheduling solver... | Confusing internal algorithm description. | Creating exam timetable and assigning rooms... | No |
| Success Message | Solved successfully: N exams scheduled with zero violations! | Jargon-heavy success alert. | Timetable created successfully: N exams scheduled without any conflicts! | No |
| Action Button | Publish Schedule | Inconsistent with "Timetable". | Publish Timetable | No |
| Read-Only Notice | Read-Only Perspective: Active role is LEARNER. Operational actions require EXAM_OFFICER... | Verbose system diagnostic text. | View-Only Mode: You are signed in as a student or guest. Creating or publishing timetables requires Exam Officer or Administrator permissions. | No |
| Table Column | Telemetry / "Why" button | "Telemetry" is sensor and developer terminology. | Reason / "View Reason" | No |
| Table Column | Timetable Interval | Technical phrasing. | Date & Time | No |
| Table Column | Seated Students | Passive table column. | Students Seated | No |
| Empty State | No examination assignments found... Click 'Execute Solver' to generate optimal timetable. | Jargon-filled guidance. | No exam assignments found for this timetable. Click 'Create Timetable' to assign rooms and times automatically. | No |
| Drawer Header | Algorithmic Decision Telemetry | Too technical. | Scheduling Decision Details | No |
| Drawer Section | Failure Reason Codes | Confusing code-oriented wording. | Why It Could Not Be Scheduled | No |
| Drawer Section | Selected Allocation | Stiff phrasing. | Assigned Room & Time | No |
| Drawer Section | Evaluation Telemetry | Developer debugging jargon. | Scheduling Process Summary | No |
| Modal Title | Create New Operational Scheduling Run | Heavy system jargon. | Create New Exam Timetable | No |
| Modal Error | Authorization Rejection (HTTP 403) | Shows raw HTTP status. | Action Not Allowed | No |
| Modal Field | Random Seed / Default baseline seed: 20261022. Guarantees deterministic, reproducible outcomes. | Mathematical jargon. | Schedule Seed (Advanced) / Standard seed is 20261022. Ensures the timetable generates consistently. | No |
| Modal Action | Create Run | Inconsistent terminology. | Create Timetable | No |

---

### Module 3: Examination Directory (`src/views/ExamManagement.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Subtitle | Directory of course assessments, equipment requirements, student cohort sizes, and scheduling parameters. | Dense academic jargon. | Browse and manage exams, room requirements, enrolled students, and durations. | No |
| Metric 1 | Total Examinations / Catalog cohort size | Technical phrasing. | Total Exams / Enrolled in term | No |
| Metric 2 | Standard Duration / Institution baseline | Robotic phrasing. | Standard Duration / Typical exam length | No |
| Metric 3 | Active Cohorts / Synchronized runs | Solver terminology. | Scheduled Batches / Active exam sessions | No |
| Table Header | Exam Code / Course / Duration / Enrolled / Status | Clear, but "Details" button needs an accessible label. | View Details (with aria-label) | No |
| Drawer Header | Technical & Facility Requirements | Overly formal. | Room & Equipment Needs | No |
| Drawer Body | Standard examination environment. No specialized equipment or facility requirements recorded. | Stiff wording. | Standard classroom or hall. No special equipment needed. | No |
| Drawer Body | Institutional Constraints / Strict student conflict isolation | Technical constraint phrasing. | Exam Guidelines / No student has two exams at the same time | No |

---

### Module 4: Student Registry (`src/views/StudentManagement.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Subtitle | Registry of enrolled candidates, accessibility accommodations, and individualized examination timetables. | Stiff phrasing. | View enrolled students, support requirements, and individual exam timetables. | No |
| Table Header | Student Number | Inconsistent with institutional terms. | Student ID | No |
| Action Button | Timetable | Ambiguous standalone noun. | View Timetable | No |
| Metric 1 | Total Student Body / Active academic candidates | Too verbose. | Total Students / Enrolled this term | No |
| Metric 2 | Standard Cohort / Regular examination protocol | Bureaucratic wording. | Standard Seating / Regular exam desks | No |
| Metric 3 | Accommodated / Extended time or specialized room | Passive phrasing. | Supported Students / Extra time or accessible rooms | No |
| Metric 4 | Conflict Free: 100% / Enforced by solver | Computational solver mention. | Schedule Clashes: 0 / No overlapping exams | No |
| Accommodation | Active Accessibility Accommodation / This candidate has approved accommodations... Scheduling engine automatically assigns compliant rooms. | Technical engine jargon. | Approved Student Support / This student has approved accommodations (such as extra time or an accessible room). The timetable automatically reserves suitable rooms. | No |
| Drawer Header | Confirmed Examination Timetable | Overly formal. | Confirmed Exam Schedule | No |
| Drawer Empty | No confirmed examination assignments found for this candidate in published schedules. | Long and passive. | No exams scheduled yet for this student in the published timetable. | No |

---

### Module 5: Course & Enrollment Management (`src/views/CourseManagement.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Subtitle | Academic course offerings, credit allocations, and student enrollment snapshots. | Technical database phrasing ("snapshots"). | Browse academic courses, student enrollments, and department offerings. | No |
| Metric 3 | Enrollment Density / Multi-department cross-listing | Obscure phrasing. | Class Size Distribution / Across all departments | No |
| Metric 4 | Sync Status: Frozen / Input snapshot locked | Internal data engineering terminology. | Roster Status: Ready / Course list confirmed for exam scheduling | No |
| Action Button | Enrollments | Single noun button. | View Enrollments | No |
| Drawer Header | Candidate Cohort Roster ({N} loaded) | Military/bureaucratic tone. | Enrolled Students ({N}) | No |
| Drawer Empty | No active student enrollments found for this course. | Clear, but could be friendlier. | No students currently enrolled in this course. | No |

---

### Module 6: Room & Facilities Management (`src/views/RoomManagement.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Subtitle | Campus venues, examination desk capacities, accessibility compliance, and equipment inventories. | Overly formal phrasing. | Manage examination rooms, desk capacities, accessibility features, and equipment. | No |
| Table Column | Effective Capacity | Technical terminology. | Exam Capacity | No |
| Action Button | Inspect | Sounds like police/building inspector. | View Details | No |
| Metric 1 | Total Examination Venues / Available for scheduling | Formal vocabulary. | Total Rooms / Ready for exams | No |
| Metric 2 | Total Examination Capacity / Synchronous candidate desks | Dense phrasing. | Total Exam Desks / Student seating capacity | No |
| Metric 3 | ADA Accessible Rooms / Step-free access certified | Technical abbreviation. | Accessible Rooms / Wheelchair & step-free access | No |
| Metric 4 | Computer Laboratories / Equipped with workstations | Formal phrasing. | Computer Labs / Workstations installed | No |
| Drawer Header | Venue Specification: ROOM-... | Overly technical header. | Room Details: ROOM-... | No |
| Drawer Section | Operating Windows & Closures | Engineering jargon. | Operating Hours | No |
| Drawer Body | Governed by RoomAvailability records. Solver validates that all candidate examination sessions fall strictly within active operational boundaries. | Low-level database and solver mechanics explained to administrators. | Exams are only scheduled in this room during these available hours. | No |
| Drawer Body | High-Performance Dedicated Student Terminals | Unnecessarily fancy wording for computers. | Student Computer Workstations | No |

---

### Module 7: Invigilator Management (`src/views/InvigilatorManagement.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Subtitle | Directory of certified examination proctors, availability windows, workload tracking, and shift assignments. | Dense description. | View exam invigilators, track daily workloads, and check assigned exam shifts. | No |
| Action Button | Roster | Single noun button. | View Shifts | No |
| Metric 1 | Total Invigilators / Certified academic proctors | Formal phrasing. | Total Invigilators / Exam supervision staff | No |
| Metric 2 | Staffing Ratio / Mandatory policy limit | Clear, but needs ratio explanation. | Staffing Ratio: 1:30 / Standard policy limit | No |
| Metric 3 | Double Booking: 0 / Strictly isolated by solver | Computational solver mention. | Schedule Clashes: 0 / Zero double-bookings | No |
| Metric 4 | Availability Rate / Logged in availability ledger | Database ledger jargon. | Staff Availability / Ready to supervise | No |
| Drawer Header | Staff Profile: INV-... | Generic title. | Invigilator Details: INV-... | No |
| Drawer Section | Assigned Examination Proctoring Shifts | Formal wording. | Assigned Exam Shifts | No |
| Drawer Empty | No confirmed proctoring shifts assigned to this staff member. | Slightly robotic. | No exam shifts assigned to this staff member yet. | No |

---

### Module 8: Accommodation Management (`src/views/AccommodationManagement.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Subtitle | Governance of student accessibility services, extra-time multipliers, and privacy-shielded clinical records. | Technical legalistic language. | Manage student accessibility needs, exam extra time, and specialized room support. | No |
| Table Column | Clinical Documentation / Inspect Notes | "Clinical Documentation" sounds intimidating. | Confidential Notes / View Notes | No |
| Metric 1 | Registered Accommodations / Active in Fall 2026 | Technical wording. | Active Student Accommodations / Fall 2026 Term | No |
| Metric 2 | Extended Duration / +25% or +50% time quota | Quota phrasing. | Extra Time Requests / Additional exam minutes | No |
| Metric 3 | Step-Free Access / Assigned to accessible rooms | Fine, but could be clearer. | Accessible Seating / Ground-floor or elevator rooms | No |
| Metric 4 | Privacy Protection / Active (FERPA) | Regulatory acronym alone. | Privacy Shield / Medical notes restricted | No |
| Banner | Pursuant to privacy regulations and academic ethics, medical and psychological evaluations are strictly restricted... | Overly verbose legal disclaimer. | Medical and support details are confidential and visible only to authorized administrators. | No |
| Banner | Active Simulation Role: {role} | Internal simulator terminology. | Current Role: {role} | No |
| Loading | Decrypting authorization token... | Overdramatic cryptographic jargon. | Loading confidential notes... | No |
| Redacted | [REDACTED FOR PRIVACY - AUTHORIZED PERSONNEL ONLY] | Cold, threatening tone. | [Restricted for Privacy: Only Administrators can view medical details] | No |
| Drawer Invariant | The deterministic solver guarantees that any candidate with this accommodation is scheduled with adequate room capacity... | Solver algorithm description. | Timetable Guarantee: Students with approved accommodations automatically receive extra time and accessible room seating. | No |

---

### Module 9: Exception Center (`src/views/ExceptionCenter.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Subtitle | Dedicated triage workspace for unscheduled examinations, hard-constraint rejections, and corrective telemetry. | Heavy hospital/developer jargon ("triage", "corrective telemetry"). | Review exams that could not be scheduled, understand the reasons, and find ways to resolve conflicts. | No |
| Toolbar | Evaluation Run: | Technical phrasing. | Timetable Version: | No |
| Metric 1 | Unscheduled Examinations / Requires administrative review | Fine, but can be friendlier. | Unscheduled Exams / Needs attention | No |
| Metric 2 | Hard Constraint Violations / Zero allowed in confirmed schedule | Mechanical math terminology. | Student / Room Clashes / Zero allowed | No |
| Metric 3 | Telemetry Traces / Recorded rejected evaluations | Sensor/debugging jargon. | Evaluated Options / Time slots checked | No |
| Metric 4 | Resolution Workflow: Deterministic / No silent data alterations | Technical database philosophy. | Rule Validation / Automatic verification | No |
| Table Column | Evaluated Failure Root Cause | Diagnostic programming jargon. | Why It Could Not Be Scheduled | No |
| Action Button | Investigate | Disciplinary tone. | View Details | No |
| Empty State | Zero Unscheduled Examinations / All course examinations in this scheduling run have been assigned to conflict-free time slots and compliant venues. | Formal wording. | All Exams Scheduled / Every exam in this timetable has been assigned to a suitable room and time with zero conflicts. | No |
| Drawer Header | Exception Investigation: EXAM-... | Forensic terminology. | Exam Issue Details: EXAM-... | No |
| Drawer Section | Evaluated Constraint Failures ({N} telemetry records) | Confusing developer terminology. | Checked Time Slots & Why They Failed | No |
| Primary CTA | Open Scheduling Workspace to Re-execute Run | Developer execution phrasing. | Go to Scheduling Workspace to Update Timetable | No |

---

### Module 10: Analytics & Reports (`src/views/AnalyticsReports.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Subtitle | Empirical scheduling telemetry, capacity utilization, workload distribution, and CSV/JSON data streams. | Overly academic and technical ("empirical", "telemetry", "data streams"). | View timetable performance metrics, room usage, invigilator workload, and export schedule reports. | No |
| Export Buttons | Export CSV / Export JSON | Standard, but "Download" is clearer for non-technical users. | Download CSV / Download JSON | No |
| Metric 1 | Scheduling Success Rate / Constraint satisfaction | Math term. | Scheduling Success Rate / Exams scheduled without conflicts | No |
| Metric 2 | Student Coverage / 5,000 / 5,000 enrolled | Good, but label can be clearer. | Student Coverage / All enrolled students included | No |
| Metric 3 | Seat Efficiency / Desk allocation density | Industrial engineering term. | Desk Utilization / Exam seats in use | No |
| Metric 4 | Accommodation Compliance / Zero policy deviations | Bureaucratic tone. | Student Support Needs Met / 100% compliant | No |
| Chart 1 | Venue Category Utilization / Average occupancy across examination operating windows | Complex phrasing. | Room Type Usage / Percentage of seats occupied during exam sessions | No |
| Chart 2 | Invigilator Shift Distribution / Proctor workload allocation against maximum daily limits | Formal description. | Staff Shift Distribution / How exam supervision shifts are spread among invigilators | No |
| Card Title | Operational Reconciliation Audit | Financial audit jargon. | Timetable Verification Summary | No |
| Card Item 1 | Student Room Seating Invariant / 100% Reconciled | Mathematical invariant phrasing. | Student Seating Verification / 100% Confirmed | No |
| Card Item 2 | Invigilator Staffing Ratio Invariant / 100% Compliant | "Invariant" is unnecessary. | Staff Supervision Ratio / 100% Compliant (1:30) | No |
| Card Item 3 | Hard Constraint Certification / Zero Violations | Formal system certification tone. | Exam Conflict Check / Zero Clashes | No |

---

### Module 11: Audit Trail & Activity (`src/views/AuditActivity.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Header | Audit Trail & Governance Ledger | Stiff corporate phrasing. | Activity History & Audit Log | No |
| Subtitle | Immutable log of state mutations, solver runs, approvals, publication events, and administrative actions. | Heavy database and solver jargon ("state mutations", "immutable"). | Complete record of who created, changed, approved, or published exam timetables and settings. | No |
| Action Button | Diff | Programmer shorthand. | View Details | No |
| Metric 1 | Total Audit Events / Cryptographically sequenced | Cryptographic jargon. | Total Logged Events / Recorded actions | No |
| Metric 2 | Ledger Storage: Append Only / Protected from overwrite | Low-level storage terminology. | Log Integrity: Permanent / Records cannot be modified | No |
| Metric 3 | Traceability / Actor + Role + Payload | Technical breakdown. | User Traceability / Full user and role logging | No |
| Metric 4 | Governance Status / Compliant | Bureaucratic tone. | Audit Status / Active | No |
| Drawer Section | State Mutation Payload | Internal database terminology. | Recorded Changes & Details | No |
| Drawer Notice | Non-Repudiation Assurance: This record is written synchronously during transaction commit... | Legalistic and technical database jargon. | Tamper-Proof Record: This entry was saved automatically when the action happened and cannot be modified or deleted. | No |

---

### Module 12: Administration & Configuration (`src/views/Administration.jsx`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Header | Administration & Policy Governance | Overly formal. | Administration & Settings | No |
| Subtitle | Institutional configuration parameters, user role permissions, and academic period rules. | Stiff phrasing. | Manage user accounts, view scheduling rules, and check institutional examination settings. | No |
| Badge | Active Role Context: {role} | Awkward phrase. | Current Role: {role} | No |
| Tab 1 | User Accounts & Access Control | Standard, but can be friendlier. | User Accounts & Permissions | No |
| Tab 2 | Scheduling Rules & Constraints | Jargon word "constraints". | Scheduling Rules & Limits | No |
| Tab 3 | Institutional Parameters | Formal term. | College Settings | No |
| Action Button | Assume Role | Stiff acting/legal term. | Switch to Role | No |
| Metric 1 | Registered Operators / Platform user profiles | Technical system phrasing. | User Accounts / Registered administrators & staff | No |
| Metric 2 | Role Hierarchy: RBAC Enforced | Developer acronym alone. | Access Control: Role-Based / Protected by user role | No |
| Metric 3 | Session Security: JWT Bearer | Raw tech acronym. | Security: Encrypted Token / Secure session | No |
| Metric 4 | Audit Non-Repudiation: Synchronous | High-level legalistic tech term. | Audit Logging: Automatic / All changes tracked | No |
| Section 1 Title | Hard Constraints (Uncompromising Invariants) | Math/computer science jargon. | Mandatory Rules (Must Never Be Broken) | No |
| Rule 1 | Student Conflict Prohibition | Negative academic jargon. | 1. No Overlapping Exams for Any Student | No |
| Rule 2 | Venue Capacity Strict Bound | Mathematical bound wording. | 2. Never Exceed Room Capacity | No |
| Rule 3 | Invigilator Non-Overlapping Bound | Stiff phrasing. | 3. No Invigilator Double-Booking | No |
| Rule 4 | Operating Hours & Availability | Clear, but description can be simpler. | 4. Exams Only During Open Hours | No |
| Rule 5 | Accessibility Accommodations | Description has solver jargon. | 5. Always Fulfill Student Support & Extra Time | No |
| Section 2 Title | Soft Optimization Heuristics | Operations research jargon. | Quality Guidelines (Best Practices) | No |
| Guideline 1 | Student Exam Spread Penalty | Optimization solver penalty phrasing. | Spread Out Student Exams | No |
| Guideline 2 | Venue Fill Density Maximization | Operations research wording. | Efficient Room Usage | No |
| Guideline 3 | Invigilator Workload Balance | Good, simplified description. | Fair Staff Workload | No |

---

### Navigation & Layout Components (`src/components/layout/`)

| Location | Existing Text | Issue | Recommended Replacement | Affects Logic? |
|---|---|---|---|---|
| Sidebar Group | Academic Master | Database master data concept. | Academic Records | No |
| Sidebar Group | Governance | Vague corporate term. | Audit & Governance | No |
| Sidebar Footer | Current Perspective | Confusing term for role. | Active Role Preview | No |
| TopNav Dropdown | Simulate Perspective | Developer simulation phrasing. | Preview Role Experience | No |
| TopNav Subtitle | System Online | Good, clear status. | System Online (Retained) | No |

---

## 4. Assessment of Impact on Application Functionality

- **API Endpoints:** None changed. All payload keys, parameter names, and URL routes remain 100% unaltered.
- **Database Schema:** None changed. IDs, enums (`DRAFT`, `PUBLISHED`, etc.) are mapped to human labels only at render time.
- **Authentication & RBAC:** Intact. Role permissions (`EXAM_OFFICER`, `ACADEMIC_ADMINISTRATOR`, etc.) continue to gate actions as before, with clearer error messages when an unauthorized action is attempted.
- **Performance:** Zero impact. String replacements and accessible helper labels are lightweight pure React changes.

