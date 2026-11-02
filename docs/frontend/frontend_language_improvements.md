# ExamOps Frontend Language Improvements Guide

**Version:** 1.0.0  
**Date:** November 2026  
**Audience:** Product Managers, Frontend Engineers, Academic Administrators  
**Objective:** Establish definitive language rules, human-first error translations, and domain terminology standards for the ExamOps platform.

---

## 1. Core Principles of ExamOps Simplified Communication

ExamOps serves university deans, examination officers, departmental administrators, invigilators, and students. To ensure trust and effortless operation:

1. **Speak the User's Language:** Use terms standard in higher education administration (e.g. *Timetable, Room, Enrolled Students, Staff Shift*), never software architecture terms (*Entity, Payload, Invariant, Deterministic Solver, Telemetry*).
2. **Keep Sentences Short & Clear:** Write direct, active sentences. Avoid passive bureaucratese.
3. **Action-Oriented Buttons:** Every button starts with an imperative action verb (*Create Timetable, Download CSV, View Details, Switch Role*).
4. **Actionable Errors:** When something goes wrong, state:
   - What happened in plain English.
   - Why it happened.
   - What specific step the user should take next.
5. **No Technical Leaks:** Never display raw HTTP codes (e.g. "HTTP 403 Forbidden"), SQL queries, database field names, or stack traces in the UI.

---

## 2. Preserved Domain Terminology & Helper Explanations

Certain higher education concepts are accurate and essential to the academic process. We preserve them, but accompany them with concise, friendly helper explanations:

| Domain Term | Definition in ExamOps | In-App Helper Tooltip or Subtext |
|---|---|---|
| **Examination** | An official course assessment scheduled in a designated venue with assigned invigilators. | "Scheduled final or midterm exam session." |
| **Invigilator** | A qualified academic or administrative proctor responsible for supervising students during an exam. | "Staff member supervising the examination room." |
| **Timetable** | The official academic schedule assigning each exam to a specific date, time slot, and room. | "Published master schedule of all campus exam sessions." |
| **Accommodation** | An approved adjustment for students with accessibility or health requirements. | "Support such as extra exam time or step-free accessible rooms." |
| **Enrollment** | A student's registered status in a course that entitles them to take that course's examination. | "Registered students assigned to take this examination." |
| **Academic Period** | The semester or term during which courses and examinations occur. | "Current academic term (e.g., Fall 2026)." |

---

## 3. Human-First Error & Alert Translation Matrix

When API responses or validation checks return technical codes, the frontend translates them into actionable guidance:

| Technical Origin / Raw Message | User-Facing Translated Message | Suggested Resolution |
|---|---|---|
| `HTTP 403 Forbidden` / `Lacks permission` | **Action Not Allowed**<br>"You do not have permission to perform this administrative action." | "Please sign in as an Exam Officer or Academic Administrator to make changes." |
| `HTTP 404 Not Found` | **Record Not Found**<br>"The requested exam, student, or room record could not be found." | "Check the ID or search query, or refresh the page." |
| `Failed to fetch` / `NetworkError` | **Unable to Connect to Server**<br>"We could not reach the ExamOps server." | "Please check your internet connection or verify the backend service is running." |
| `Constraint violation: STUDENT_CONFLICT` | **Student Exam Clash Detected**<br>"This exam cannot be scheduled at this time because enrolled students have another exam scheduled simultaneously." | "Choose an alternate time slot or day for this exam." |
| `Constraint violation: CAPACITY_EXCEEDED` | **Room Capacity Exceeded**<br>"The enrolled student cohort is larger than the available desk capacity of this room." | "Select a larger venue or split the exam across multiple adjacent rooms." |
| `Constraint violation: INVIGILATOR_DOUBLE_BOOKED` | **Invigilator Already Scheduled**<br>"The selected staff member is already supervising another room during this time slot." | "Assign an alternate invigilator who is available for this session." |
| `Constraint violation: ACCOMMODATION_IGNORED` | **Student Support Requirement Missing**<br>"This room does not satisfy the accessibility needs of one or more enrolled candidates." | "Assign an accessible room or grant the required extra examination minutes." |
| `Constraint violation: OUTSIDE_OPERATING_HOURS` | **Outside Room Operating Hours**<br>"The selected examination time extends past the building's operating hours." | "Reschedule the exam between 08:00 and 18:00 or update venue hours." |

---

## 4. Status Badge Standard Vocabulary

All status badges in `StatusBadge.jsx` are translated from raw database uppercase enums into clean, title-cased labels with matching Outskill theme colors:

```javascript
export const STATUS_LABELS = {
  // Scheduling Runs
  DRAFT: 'Draft',
  SCHEDULING: 'Scheduling...',
  REVIEW_REQUIRED: 'Needs Review',
  APPROVED: 'Approved',
  PUBLISHED: 'Published',
  SUPERSEDED: 'Archived',
  CANCELLED: 'Cancelled',

  // Master Data
  ACTIVE: 'Active',
  AVAILABLE: 'Available',
  CONFIRMED: 'Confirmed',
  READY: 'Ready',
  INACTIVE: 'Inactive',
  SUSPENDED: 'Suspended',

  // Severity & Issues
  INFO: 'Info',
  WARNING: 'Warning',
  ERROR: 'Error',
  BLOCKER: 'Urgent Issue',
  CRITICAL: 'Critical',
  BLOCKING: 'Unscheduled',
};
```

---

## 5. Module-by-Module Before & After Transformation

### Module 1: Overview Dashboard
- **Before:** "Current Operational Schedule State" / "Authoritative schedule output for the active semester" / "Feasibility yield: 98.7%"
- **After:** "Current Timetable Status" / "Official timetable for this academic term" / "Scheduling Success: 98.7%"

### Module 2: Scheduling Workspace
- **Before:** Button "Execute Solver" / "Run: RUN-2026-001" / Drawer "Algorithmic Decision Telemetry"
- **After:** Button "Create Timetable" / "Timetable Version: RUN-2026-001" / Drawer "Scheduling Decision Details"

### Module 3: Exam Management
- **Before:** "Directory of course assessments, equipment requirements, student cohort sizes, and scheduling parameters."
- **After:** "Browse and manage exams, room requirements, enrolled students, and durations."

### Module 4: Student Management
- **Before:** Column "Student Number" / Metric "Regular examination protocol" / "Enforced by solver"
- **After:** Column "Student ID" / Metric "Standard Seating" / "Zero Exam Clashes"

### Module 5: Course & Enrollment Management
- **Before:** "Input snapshot locked" / "Candidate Cohort Roster (50 loaded)"
- **After:** "Course list confirmed for exam scheduling" / "Enrolled Students (50)"

### Module 6: Room & Facilities Management
- **Before:** Column "Effective Capacity" / Button "Inspect" / "Operating Windows & Closures"
- **After:** Column "Exam Capacity" / Button "View Details" / "Operating Hours"

### Module 7: Invigilator Management
- **Before:** Button "Roster" / Metric "Certified academic proctors" / "Assigned Examination Proctoring Shifts"
- **After:** Button "View Shifts" / Metric "Exam supervision staff" / "Assigned Exam Shifts"

### Module 8: Accommodation Management
- **Before:** Column "Clinical Documentation" / Button "Inspect Notes" / "Decrypting authorization token..."
- **After:** Column "Confidential Notes" / Button "View Notes" / "Loading confidential notes..."

### Module 9: Exception Center
- **Before:** "Dedicated triage workspace for unscheduled examinations, hard-constraint rejections, and corrective telemetry."
- **After:** "Review exams that could not be scheduled, understand the reasons, and find ways to resolve conflicts."

### Module 10: Analytics & Reports
- **Before:** Buttons "Export CSV" / "Export JSON" / "Operational Reconciliation Audit" / "Student Room Seating Invariant"
- **After:** Buttons "Download CSV" / "Download JSON" / "Timetable Verification Summary" / "Student Seating Verification"

### Module 11: Audit Activity
- **Before:** "Audit Trail & Governance Ledger" / "State Mutation Payload" / "Diff"
- **After:** "Activity History & Audit Log" / "Recorded Changes & Details" / "View Details"

### Module 12: Administration
- **Before:** "Administration & Policy Governance" / "Hard Constraints (Uncompromising Invariants)" / "Soft Optimization Heuristics"
- **After:** "Administration & Settings" / "Mandatory Rules (Must Never Be Broken)" / "Quality Guidelines (Best Practices)"

