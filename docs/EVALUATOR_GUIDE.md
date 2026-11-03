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

## 2. Evaluator Demonstration Credentials

An active, verified **Academic Administrator** account has been provisioned in the live database for external project review.

To protect the live demonstration environment, the password is not committed to the public Git repository.

| Field | Configuration | Notes |
|---|---|---|
| **Institutional Email** | `evaluator@examops.edu` | Dedicated demonstration user |
| **Password** | `[SECURE_SUBMISSION_PASSWORD]` | *Supplied securely in evaluation submission brief* |
| **Assigned Role** | `ACADEMIC_ADMINISTRATOR` | Full operational and scheduling privileges |
| **Display Name** | `ExamOps Evaluator` | Audit and log actor identity |
| **Account Status** | `ACTIVE` | Verified operational status |
| **Database Identity** | `auth.users` UUID (`d88e966e-d605-40b0-8213-fa40e63e9f98`) | Mapped to `public.user_profiles` |

### Secure Credential Distribution Procedure
- **Private Delivery**: The project owner securely shares the provisioned evaluator password through the confidential project submission portal or private candidate-evaluator communication channel.
- **Zero Secrets in Repository**: No plaintext passwords, service-role keys, or JWT secrets are stored in Git version control.
- **Credential Rotation**: The project owner can rotate the evaluator password on demand using the server-side provisioning script with environment variables.

---

## 3. Quick-Start Login Walkthrough

1. Open **[https://exam-ops-murex.vercel.app](https://exam-ops-murex.vercel.app)** in any modern desktop or mobile browser.
2. If unauthenticated, the application automatically redirects to the secure enterprise login screen (`/login`).
3. Enter the evaluator email and password:
   - **Email**: `evaluator@examops.edu`
   - **Password**: *(The provisioned evaluator password provided in your evaluation brief)*
     *(Click the Eye icon in the input field to toggle password visibility if desired).*
4. Click **Sign In**.
5. Upon cryptographic token verification against Supabase Auth, the application securely resolves your database profile and transitions directly to the **Overview Dashboard**.
6. When finished reviewing, click the **Sign Out** button located in the top-right navigation bar (or sidebar footer on mobile) to terminate your session and return to `/login`.

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
