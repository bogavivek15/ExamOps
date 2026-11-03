# ExamOps — External Evaluator & Project Review Guide

> **Product**: ExamOps (Examination Operations & Intelligent Scheduling Platform)
> **Evaluation Mode**: External Technical Review & Interactive Verification
> **Deployment Architecture**: Vercel (Frontend) + Render (FastAPI Backend) + Supabase (PostgreSQL & Auth)

---

## 1. Live Deployment Endpoints

| Service Tier | Live Production URL | Description |
|---|---|---|
| **Web Application** | [https://exam-ops-murex.vercel.app](https://exam-ops-murex.vercel.app) | React 19 + Vite enterprise dark-first interface |
| **Backend API** | [https://examops-4x4l.onrender.com](https://examops-4x4l.onrender.com) | FastAPI REST service with automated Swagger docs |
| **API Health Check** | [https://examops-4x4l.onrender.com/health](https://examops-4x4l.onrender.com/health) | Live service heartbeat & database connectivity probe |
| **Interactive API Docs** | [https://examops-4x4l.onrender.com/docs](https://examops-4x4l.onrender.com/docs) | OpenAPI interactive documentation |

---

## 2. Evaluator Access Architecture & Roles

ExamOps features a streamlined, centered login experience supporting all **five primary system actors**:

| Actor / Persona | Mode | Synthetic Identity | Operational Scope & Access Boundary |
|---|---|---|---|
| **Academic Administrator** | Demo (Passwordless) | evaluator@examops.edu | Full examination operations: scheduling workspace, solver execution, timetable publication, room allocations, exception triage, and audit trail inspection. |
| **Instructor** | Demo (Passwordless) | head.computer@faculty.institution.edu | View assigned courses, examination timetables, and academic schedule data. Strictly restricted from invigilator schedules, proctor availability, and clinical accommodation notes. |
| **Support Staff** | Demo (Passwordless) | acilities.lead.1@examops.institution.edu | Facilities and operational support: room capacities, venue equipment, maintenance closures, availability, and validation triage. Restricted from academic scheduling approval and user security administration. |
| **Learner** | Demo (Passwordless) | carlos.garcia.0008@student.institution.edu | View personal examination timetable and approved accommodation details. Strictly isolated to own data; cannot access other learners' records, modify schedules, or view admin operations. |
| **Platform Administrator** | Protected (Credentials) | dmin@examops.institution.edu | Platform-level security, user profiles, RBAC role assignments, and system-wide configuration. Strictly requires institutional credentials. |

---

## 3. Quick-Start Login Walkthrough

1. Open **[https://exam-ops-murex.vercel.app](https://exam-ops-murex.vercel.app)** in any modern desktop or mobile browser.
2. The application loads the minimal, centered login card with the signature lime-green ExamOps branding.
3. Select any role from the **Select Role** dropdown:
   - For complete exam officer evaluation: Select **Academic Administrator**.
   - The button dynamically updates to **Login as Academic Administrator**.
4. Click **Login as Academic Administrator** to enter directly without typing an email or password.
5. Upon token generation and database profile resolution, the application securely logs you in and transitions to the **Overview Dashboard**.
6. When testing role boundaries, click **Sign Out** from the profile menu and select **Instructor**, **Support Staff**, or **Learner** to test each persona's role-scoped views and permissions.
7. To access **Platform Administrator**, select it in the dropdown, enter valid institutional administrator credentials, and authenticate.
---

## 4. Platform Tour: 12 Operational Modules

Once signed in, access all modules through the collapsible left navigation sidebar:

### Module 1: Overview Dashboard (`/`)
- **Key Metrics**: Real-time snapshot of the institution's examination profile: **5,000 students**, **300 examinations**, **100 rooms**, **200 invigilators**, and active accommodations.
- **Progress Tracking**: Overall scheduling completion percentage, seated student headcount, and seat utilization metrics derived from actual database records.

### Module 2: Scheduling Operations Center (`/scheduling`)
- **Operations Center**: The core scheduling command interface.
- **Timetable & Allocations**: Inspect scheduled examination blocks mapped to specific dates, time slots, and physical rooms.
- **Explainability**: Click on individual assignments to view the solver's constraint telemetry—why a particular room and slot were chosen, and which alternative options were rejected.

### Module 3: Examination Management (`/exams`)
- **Directory**: Comprehensive table of all 300 academic examinations.
- **Details**: Inspect duration (minutes), required equipment (e.g., Computer Lab, Projector), priority levels, and student enrollment cohorts.

### Module 4: Student Registry (`/students`)
- **Registry**: Search and filter among 5,000 enrolled students.
- **Timetable Inspection**: Select any student to review their individual examination schedule and verify that zero overlapping examinations occur.

### Module 5: Course & Enrollment Management (`/courses`)
- **Curriculum Records**: Course catalog, academic departments, and enrollment mappings.

### Module 6: Rooms & Facilities (`/rooms`)
- **Venue Management**: 100 examination rooms with effective capacities, wheelchair accessibility flags, and AV equipment inventories.

### Module 7: Invigilator Management (`/invigilators`)
- **Proctor Allocation**: 200 staff profiles, availability time-windows, maximum daily/weekly working hours, and assignment history.

### Module 8: Accommodation Management (`/accommodations`)
- **Special Arrangements**: Extra writing time (e.g., +30 min), low-distraction seating, wheelchair-accessible venues, and assistive equipment.
- **FERPA Privacy**: Clinical health notes are masked and isolated to authorized personnel.

### Module 9: Issue & Conflict Center (`/exceptions`)
- **Exception Investigation**: Dedicated workspace for unassigned examinations.
- **Traceable Root Cause Codes**: Every unscheduled exam includes an explicit reason code (e.g., `CONFLICT_STUDENT_OVERLAP`, `CAPACITY_EXCEEDED`, `NO_ROOM_AVAILABLE`).

### Module 10: Analytics & Reports (`/analytics`)
- **Operational Auditing**: Seat utilization histograms, invigilator workload distribution, and accommodation compliance rates.
- **Exporting**: Export datasets directly to **CSV** and **JSON** for external institutional reporting.

### Module 11: Audit & Activity (`/audit`)
- **Immutable Log**: Append-only log of operational events, run executions, and approval state transitions.

### Module 12: Administration (`/admin`)
- **Institutional Governance**: Operating hours, default time-slot intervals, staffing ratios, and academic term boundaries.

---

## 5. Security & Verification Architecture

ExamOps enforces an enterprise-grade security perimeter:

1. **Supabase Auth Integration**:
   - Authentication is performed via Supabase Auth (`auth.users` and `auth.identities`).
   - Tokens are cryptographically verified using Supabase Auth's RFC 7517 JWKS endpoint (`ES256`/`RS256` asymmetric keys) or authenticated user verification.
2. **Database-Authoritative RBAC**:
   - The user's role is never accepted from client-side claims, URL parameters, or untrusted headers.
   - FastAPI queries the active `user_profiles` record in PostgreSQL for every authenticated request.
   - Inactive or suspended accounts are rejected immediately with HTTP 401.
3. **Session Revocation (5-Second SLA)**:
   - User profile lookups utilize an in-memory cache with a strict 5.0-second TTL. Role changes or account deactivations take effect globally across all workers within 5 seconds.
4. **OWASP Compliance**:
   - `nosniff`, `DENY` frame-options (clickjacking protection), and strict CORS origin matching configured for `https://exam-ops-murex.vercel.app`.
   - Insecure development bypasses (`/api/auth/dev-switch-role`) are blocked in production with HTTP 403.

---

## 6. Safe Operations for Evaluators

Evaluators are invited to test:
- **Authentication**: Sign in, sign out, attempt invalid passwords, refresh browser to verify session persistence.
- **Data Filtering & Search**: Search students, exams, rooms, and invigilators by department, status, or keyword.
- **Telemetry Inspection**: Click into scheduling assignments to review the decision rationales and constraint checks.
- **Export**: Generate CSV or JSON exports from the Analytics module.

---

## 7. Account Re-Provisioning (For Project Administrators)

If the evaluator password needs to be rotated or re-provisioned, run the server-side provisioning script using environment variables:

```bash
# Set credentials securely via environment variables
export EVALUATOR_EMAIL="evaluator@examops.edu"
export EVALUATOR_PASSWORD="<YourSecurePasswordHere>"

# Execute provisioning script
python scripts/provision_evaluator.py
```

The script verifies table constraints, synchronizes `auth.users` and `auth.identities`, and upserts the active `user_profiles` record without storing credentials in files.
