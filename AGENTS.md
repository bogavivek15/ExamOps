# EXAMOPS
# DEFINITIVE MASTER PRODUCT & ENGINEERING SPECIFICATION

Version: 1.0.0  
Product: ExamOps  
Full name: Examination Operations & Intelligent Scheduling Platform  
Project type: Full-stack enterprise application  
Workspace: New project from scratch  
IDE: Google Antigravity  
Primary objective: Build a complete, reliable, exceptionally designed and technically explainable examination operations platform.

================================================================
01. PROJECT MANDATE
================================================================

You are the principal engineering agent responsible for designing, building, testing and delivering ExamOps.

You must take responsibility for the complete product lifecycle:

1. Understanding the business problem.
2. Translating requirements into technical contracts.
3. Designing the relational database.
4. Generating realistic synthetic data.
5. Implementing the scheduling algorithm.
6. Building backend APIs.
7. Building the React application.
8. Integrating authentication and authorization.
9. Implementing auditability and traceability.
10. Validating every hard constraint.
11. Testing the complete application.
12. Deploying the application.
13. Preparing documentation and the public repository.

Think like a senior product engineer, not an autocomplete system.

Do not merely produce code that looks convincing.

Implement functionality, execute it, inspect its results and prove that it works.

### The primary success criteria

A. The application looks like premium commercial enterprise software.

B. Every mandatory business requirement is implemented.

C. The database contains valid, consistent and reproducible data.

D. The scheduling engine produces valid, explainable decisions.

E. Every unscheduled examination has documented reasons.

F. No invalid schedule can be approved or published.

G. Important decisions and state changes are traceable.

H. The application works with actual database records.

I. Testing verifies behavior rather than merely checking that files exist.

J. The candidate can explain the complete implementation in an interview.

### Ownership principle

The candidate is the product owner.

You are responsible for implementation and technical recommendations.

Do not silently make critical academic-policy decisions.

Do not repeatedly ask questions whose answers are already established.

When a business rule is unspecified, recommend a reasonable configurable default, explain it and record it as an assumption.

Ask only questions that materially affect correctness or institutional policy.

================================================================
02. AUTHORITATIVE SOURCE REQUIREMENTS
================================================================

The original YottaFlex problem statement is the authoritative business specification.

The following are also authoritative submission sources:

- Candidate Project FAQ.
- Candidate Project Submission Guidelines.

At the beginning of the project, inspect the source documents provided in:

docs/source/

Expected files:

- problem_statement.md
- candidate_faq.pdf
- submission_guidelines.pdf

If a file is not present, do not pretend to have read it. Request that it be placed in the workspace.

Extract the original requirements and preserve their meaning.

Create a requirements register with:

- Requirement ID.
- Original requirement.
- Requirement category.
- Business interpretation.
- Affected entities.
- Implementation module.
- Verification method.
- Acceptance condition.
- Current status.

Separate:

1. Explicit source requirements.
2. Candidate-approved assumptions.
3. Recommended technical decisions.
4. Optional product improvements.

Never let optional improvements displace mandatory requirements.

### Mandatory requirements that must be preserved

MASTER DATA:
- Student.
- Course.
- Enrollment.
- Exam.
- ExamRequirement.

DEPENDENT DATA:
- Room.
- RoomCapacity.
- Invigilator.
- Availability.
- Accommodation.
- ScheduleAssignment.

WORKFLOW:
- Generate master data first.
- Generate child records with valid parent IDs.
- Build enrollments.
- Generate exams and duration requirements.
- Define rooms, capacities and equipment.
- Define invigilator availability.
- Define student accommodations.
- Build the conflict graph.
- Assign examinations to times and rooms.
- Report unassigned examinations and reason codes.

STATE MANAGEMENT:
- Preserve important state changes as explicit records/events.
- Do not overwrite history.
- Generate ground truth from documented rules.
- Keep ground truth out of operational inputs.

DATA GENERATION:
- 5,000 students.
- 300 exams.
- 100 rooms.
- 200 invigilators.
- Fixed seed 20261022.
- Starter and full profiles using the same generator.

REQUIRED NEGATIVE SCENARIOS:
1. Student has overlapping exams.
2. Room capacity exceeded.
3. Invigilator double-booked.
4. Accommodation ignored.
5. Exam outside room availability.

ACCEPTANCE:
- No hard constraint violated in confirmed assignments.
- Every unscheduled examination has a reason.
- Room and invigilator usage reconciles.
- Accommodations are enforced consistently.
- Relationships are valid.
- IDs are consistent.
- Derived values are calculated.
- Ground truth is separate.
- Generation is reproducible.
- Documentation and validation evidence exist.

Do not omit any of these.

================================================================
03. FIXED TECHNOLOGY STACK
================================================================

The stack has already been selected.

Do not repeatedly suggest a different framework.

### Frontend

React + Vite + JavaScript + Tailwind CSS.

Use:

- React.
- Vite.
- JavaScript.
- Tailwind CSS.
- React Router.
- Lucide React.
- Supabase JavaScript client.
- Recharts for meaningful charts only.
- Native React hooks and Context.
- Native fetch API.

Use plain CSS where it creates a better design result.

Do not use Next.js.

Do not use TypeScript.

Do not introduce Redux.

Do not introduce a complex state-management system.

Do not introduce a form library unless a concrete need is demonstrated.

### Backend

Python + FastAPI.

Use:

- Python.
- FastAPI.
- Pydantic.
- Supabase Python SDK.
- Python standard library for scheduling and data generation.
- Pytest for testing.

### Database

Supabase PostgreSQL.

Use:

- Supabase Auth.
- PostgreSQL.
- Row Level Security.
- SQL migration files.
- Supabase client libraries.

### Deployment

- Vercel: frontend.
- Render: FastAPI backend.
- Supabase: database and authentication.

### Important technology restrictions

Do not introduce:

- OR-Tools.
- LangChain.
- LangGraph.
- Redis.
- Celery.
- Kafka.
- Prisma.
- SQLAlchemy.
- Microservices.
- Vector databases.
- Machine learning frameworks.
- LLM-based scheduling.
- Unnecessary Docker infrastructure.

Do not add technologies just to make the project look advanced.

The candidate must be able to explain how every major dependency works.

Use the fewest dependencies necessary.

Before installing a dependency, document what it does and why the existing stack cannot reasonably handle the task.

================================================================
04. PRODUCT IDENTITY
================================================================

Brand: ExamOps.

Product category: Examination Operations Management.

Product description:

An integrated platform for academic institutions to manage the entire examination scheduling lifecycle, from student enrollment and examination requirements to resource allocation, exception management, schedule publication and audit.

Tagline:

"Plan Smarter. Schedule Precisely. Operate With Confidence."

The identity should communicate:

- Reliability.
- Accuracy.
- Organization.
- Professionalism.
- Operational intelligence.
- Institutional trust.

Build a recognizable visual identity.

Do not make the application resemble a generic AI-generated dashboard.

================================================================
05. UI/UX DESIGN CONTRACT
================================================================

Visual and interaction quality are major product requirements.

The application must feel like a premium enterprise SaaS product designed by a professional product team.

Do not prioritize decorative effects over information architecture.

### 5.1 Visual direction

Premium dark-first enterprise interface.

Recommended palette:

- Background: #0B1118.
- Sidebar: #0E151D.
- Surface: #121C26.
- Elevated surface: #172330.
- Border: #263442.
- Main text: #E8EEF5.
- Secondary text: #9AAABA.
- Primary accent: #56D6C2.
- Success: #57BE93.
- Warning: #E8B66D.
- Danger: #E87979.
- Information: #7CAAE5.

These are initial design tokens.

Verify contrast and accessibility before finalizing the palette.

Centralize all tokens.

### 5.2 Typography and hierarchy

Use a carefully selected professional sans-serif.

Prefer Inter or Geist when licensing and availability are appropriate.

Establish:

- Heading hierarchy.
- Body typography.
- Table typography.
- Supporting text.
- Metric typography.
- Tabular number styling.

Do not use oversized headings in every section.

### 5.3 Visual quality requirements

Use:

- Refined spacing.
- Consistent alignment.
- Subtle borders.
- Controlled surfaces.
- Professional tables.
- Sophisticated calendar layouts.
- Restrained shadows.
- Clear status indicators.
- High-quality forms.
- Contextual interactions.
- Meaningful data visualization.

Avoid:

- Excessive gradients.
- Glassmorphism everywhere.
- Neon colors.
- Decorative floating shapes.
- Huge rounded cards.
- Excessive animations.
- Repeated metric-card layouts.
- Emoji-based interface icons.
- Generic template aesthetics.
- Fake charts.
- Placeholder buttons.

### 5.4 Reference quality

Use the product quality of Linear, Stripe, Vercel and modern enterprise operations platforms as inspiration.

Study:

- Information density.
- Navigation.
- Typography.
- Interaction behavior.
- Table quality.
- Visual hierarchy.
- Micro-interactions.

Do not copy their interfaces.

### 5.5 Application layout

Desktop structure:

LEFT SIDEBAR:
- ExamOps brand.
- Primary navigation.
- Navigation groups.
- Active state.
- Collapse functionality.

TOP BAR:
- Breadcrumb.
- Current page context.
- Global search.
- Academic period selector.
- Notifications.
- User menu.

MAIN:
- Contextual page content.
- Page-specific actions.
- Filters.
- Data tables.
- Calendar.
- Analytics.

DETAIL PANEL:
- Contextual record details.
- Scheduling explanations.
- Exception investigation.
- Assignment inspection.

Do not force the same layout on every page.

### 5.6 Reusable components

Create a consistent component system:

- AppSidebar.
- TopNavigation.
- PageHeader.
- Breadcrumbs.
- Button.
- Input.
- Select.
- SearchInput.
- DateInput.
- DataTable.
- FilterBar.
- Pagination.
- StatusBadge.
- Modal.
- Drawer.
- Toast.
- Tabs.
- ConfirmationDialog.
- EmptyState.
- LoadingState.
- ErrorState.
- Calendar.
- Timeline.
- MetricDisplay.
- ChartContainer.

Avoid component duplication.

Avoid giant monolithic page files.

### 5.7 Interaction requirements

Every user action must work.

Include:

- Input validation.
- Search.
- Sorting.
- Filtering.
- Pagination.
- Confirmation dialogs.
- Loading feedback.
- Error feedback.
- Success feedback.
- Keyboard accessibility.
- Focus management.
- Responsive behavior.

Every button must have a defined functional outcome.

Never use a fake button simply to make a screen look complete.

### 5.8 Responsive design

Ensure usability at:

- Desktop.
- Tablet.
- Mobile.

Desktop is the primary operational experience.

Test tables, forms, calendars, drawers, modals and navigation on smaller screens.

Support reduced motion and appropriate accessibility contrast.

================================================================
06. COMPLETE PRODUCT MODULES
================================================================

The product must include the following operational areas.

### MODULE 1 — OVERVIEW DASHBOARD

Purpose: Show the operational condition of the institution's examination schedule.

Display:

- Total students.
- Total courses.
- Total examinations.
- Scheduled examinations.
- Unassigned examinations.
- Scheduling completion.
- Student coverage.
- Room utilization.
- Seat utilization.
- Invigilator utilization.
- Accommodation compliance.
- Active scheduling runs.
- Open exceptions.
- Upcoming examinations.
- Recent activities.

Provide:
- Academic period filter.
- Date range filter where useful.
- Published/draft context.

Every number must be derived from real data.

### MODULE 2 — SCHEDULING WORKSPACE

This is the most important screen.

Build a premium examination operations command center.

It must include:

- Calendar.
- Timetable.
- Examination listing.
- Time-slot filtering.
- Room allocation.
- Invigilator assignment.
- Student conflict detection.
- Accommodation indicators.
- Room availability.
- Invigilator availability.
- Scheduling execution.
- Scheduling results.
- Assignment inspection.
- Unassigned examination inspection.
- Exception links.
- Validation summary.
- Approval.
- Publication.

For every examination, show:

- Enrollment count.
- Course.
- Duration.
- Required equipment.
- Required accommodations.
- Conflict count.
- Selected time.
- Selected room or rooms.
- Assigned invigilators.
- Assignment status.

For every scheduling decision, display:
- What was evaluated.
- Which constraints passed.
- Which constraints failed.
- Why the chosen candidate was selected.
- Why alternatives were rejected.

Make this experience more detailed and polished than a normal CRUD calendar.

### MODULE 3 — EXAMINATION MANAGEMENT

Implement:

- Examination directory.
- Search.
- Filters.
- Sorting.
- Pagination.
- Create.
- Edit.
- Details.
- Course association.
- Enrollment count.
- Duration requirements.
- Equipment requirements.
- Priority.
- Lifecycle status.
- Scheduling history.

### MODULE 4 — STUDENT MANAGEMENT

Implement:

- Student directory.
- Student details.
- Course enrollment.
- Examination participation.
- Conflict information.
- Accommodation status.

Protect sensitive student information.

### MODULE 5 — COURSE AND ENROLLMENT MANAGEMENT

Implement:

- Course creation.
- Course editing.
- Course directory.
- Enrollment creation.
- Enrollment updates.
- Enrollment status.
- Academic period.
- Student-course relationship validation.

### MODULE 6 — ROOM MANAGEMENT

Implement:

- Room directory.
- Room creation and editing.
- Capacity.
- Capacity history.
- Equipment.
- Accessibility.
- Operating hours.
- Availability.
- Closures.
- Utilization.
- Assignment history.

### MODULE 7 — INVIGILATOR MANAGEMENT

Implement:

- Directory.
- Profiles.
- Availability.
- Unavailability periods.
- Workload.
- Assignment history.
- Double-booking indicators.
- Relevant qualifications where applicable.

### MODULE 8 — ACCOMMODATION MANAGEMENT

Implement configurable types:

- Extended examination time.
- Accessible room.
- Low-distraction room.
- Special equipment.
- Other institution-defined needs.

Support effective dates.

Limit sensitive details to authorized users.

### MODULE 9 — EXCEPTION CENTER

A dedicated issue investigation workspace.

Show:

- Exception ID.
- Examination.
- Run.
- Reason code.
- Failed constraint.
- Affected resource.
- Severity.
- Detection time.
- Explanation.
- Suggested corrective action.
- Resolution status.
- Resolution history.

Allow authorized administrators to record resolution actions.

Do not silently change source data or institutional rules.

After a source correction, reevaluate the examination through the actual scheduling process.

### MODULE 10 — ANALYTICS AND REPORTS

Implement:

- Scheduling success.
- Student coverage.
- Room utilization.
- Seat utilization.
- Invigilator utilization.
- Accommodation compliance.
- Conflict statistics.
- Exception distribution.
- Unassigned examination statistics.

Support CSV and JSON export.

### MODULE 11 — AUDIT AND ACTIVITY

Show:

- User.
- Role.
- Action.
- Entity.
- Previous state.
- New state.
- Timestamp.
- Scheduling run.
- Result.

Keep historical events protected from ordinary editing.

### MODULE 12 — ADMINISTRATION

Implement:

- User management.
- Role management.
- Academic periods.
- Time-slot policies.
- Scheduling rules.
- Institution configuration.

==================================================
07. DATABASE ENGINEERING CONTRACT
==================================================

Use Supabase PostgreSQL.

Create a normalized relational data model.

Never design tables only to suit the frontend.

### 7.1 Required entities

- Student.
- Course.
- Enrollment.
- Exam.
- ExamRequirement.
- Room.
- RoomCapacity.
- Invigilator.
- Availability.
- Accommodation.
- ScheduleAssignment.

### 7.2 Required supporting entities

Create these when required:

- AcademicPeriod.
- RoomAvailability.
- RoomEquipment.
- EquipmentType.
- AssignmentStudent.
- AssignmentInvigilator.
- SchedulingRun.
- SchedulingDecision.
- ScheduleEvent.
- ValidationIssue.
- UserProfile.
- UserRole.
- AuditLog.

Do not introduce supporting entities without documenting their purpose.

### 7.3 Entity relationship rules

Student to Course:
Many-to-many through Enrollment.

Course to Exam:
One-to-many for the initial product.

Exam to ExamRequirement:
One-to-many.

Room to RoomCapacity:
One-to-many.

Room to Equipment:
Many-to-many through RoomEquipment.

Invigilator to Availability:
One-to-many.

Room to Availability:
One-to-many through RoomAvailability.

Student to Accommodation:
One-to-many.

Exam to Room:
Many-to-many through ScheduleAssignment across scheduling runs.

ScheduleAssignment to Student:
Many-to-many through AssignmentStudent.

ScheduleAssignment to Invigilator:
Many-to-many through AssignmentInvigilator.

Document the implemented cardinalities.

### 7.4 Field-level data dictionary

For every required entity, document every field with:

- Field name.
- PostgreSQL type.
- Required or optional.
- Allowed values.
- Unit.
- Uniqueness.
- Validation.
- Primary or foreign key.
- Effective-date semantics.

Do not leave any entity as an undocumented collection of columns.

### 7.5 Identifier strategy

Use the required nomenclature:

STU-000001

EXAM-2026-000001

ROOM-000001

INV-000001

ASN-<exam-id>-<room-id>

Additional IDs may follow:

CRS-000001

ENR-000001

REQ-000001

CAP-000001

AVL-000001

ACO-000001

All IDs must be deterministic in synthetic data.

Use zero-padded counters.

Never regenerate an ID during an ordinary update.

For scheduling assignments:
- Use a database-generated UUID as the internal primary key.
- Store the required ASN value as the public assignment code.
- Enforce uniqueness on scheduling_run_id plus assignment_code.
- Preserve the same ASN naming format across runs.

This permits historical runs without creating identifier collisions.

### 7.6 Enrollment and examination participation

Eligible examination students must derive from valid enrollment records.

At scheduling-run creation:

1. Identify the applicable academic period.
2. Resolve active enrollments.
3. Derive examination participants.
4. Record a student-examination snapshot.
5. Record the source version/hash.
6. Calculate eligible student counts.
7. Freeze the run's participation inputs.

Implement a RunExamStudent snapshot table or equivalent justified structure.

A later enrollment edit must not silently alter an existing historical scheduling run.

### 7.7 Examination requirements

Represent requirements as structured records.

Examples:

- DURATION_MINUTES.
- REQUIRED_EQUIPMENT.
- ROOM_FEATURE.
- OTHER_APPROVED_REQUIREMENT.

Store:
- Requirement type.
- Value.
- Unit.
- Mandatory or optional.
- Effective period if applicable.

Validate recognized values.

### 7.8 Accommodation representation

Store:
- Student.
- Accommodation type.
- Effective start.
- Effective end.
- Numeric value where needed.
- Unit.
- Required room feature or equipment.
- Active status.

For extended duration, use explicit extra minutes or an explicitly approved percentage.

Define one consistent calculation rule.

Do not infer undocumented academic policy.

### 7.9 Room capacity

Use effective-dated RoomCapacity.

The room capacity for an exam must be determined by the examination date.

Do not rely on a single overwritten room capacity value when historical capacity matters.

### 7.10 Availability

Use Availability for invigilator availability.

Use RoomAvailability for room operating periods and closures.

Availability records must have clear start/end boundaries.

Do not overlap contradictory availability states.

### 7.11 Database integrity

Implement:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Required indexes.
- Referential integrity.
- Appropriate deletion rules.
- Transactional state changes.

Do not rely only on API validation.

### 7.12 Database migrations

Use committed SQL migrations.

Keep schema changes reproducible.

Do not manually modify the production schema without a corresponding migration.

Use Supabase CLI where appropriate.

==================================================
08. BUSINESS RULES AND ASSUMPTION REGISTER
==================================================

Separate actual source requirements from missing institution-specific policy.

The source specifies the required constraints but does not prescribe every scheduling policy.

Create a configurable business settings section.

Potential settings:

- Institution timezone.
- Academic scheduling dates.
- Operating hours.
- Examination slot interval.
- Minimum break.
- Staffing ratio.
- Maximum invigilator workload.
- Allowed resource features.
- Accommodation rules.
- Publication permissions.

Do not invent mandatory institutional values.

For each unprovided value:

1. Record the assumption.
2. Mark it as configurable.
3. Explain the reason.
4. Set a clearly labelled demo default.
5. Allow the administrator to modify it where appropriate.

Example:

max_students_per_invigilator = 30

This is only a demo configuration until confirmed by the institution. It must not be presented as an official source requirement.

Use a similar explicit approach for time slots and examination operating hours.

The candidate should approve critical assumptions once and have them recorded in docs/business_rules.md.

Do not repeatedly interrupt implementation for minor configuration preferences.

==================================================
09. SYNTHETIC DATA ENGINEERING
==================================================

Implement a standalone Python data generator.

### 9.1 Required baseline

Generate exactly:

5,000 Students.

300 Examinations.

100 Rooms.

200 Invigilators.

Also generate courses, enrollments, requirements, equipment, availability and accommodations.

The source does not prescribe exact counts for every supporting entity. Define configurable distributions and document them.

### 9.2 Seed

Use:

20261022

Use Python's standard `random.Random(seed)`.

Use stable deterministic ordering.

Avoid random UUIDs and nondeterministic values in the generated dataset.

Use deterministic ID counters.

### 9.3 Profiles

Support:

- Starter.
- Full.

Both profiles must use the same generation code.

Command examples:

python -m generator.generate --profile starter --seed 20261022

python -m generator.generate --profile full --seed 20261022

### 9.4 Generation order

1. Academic period.
2. Students.
3. Courses.
4. Rooms.
5. Invigilators.
6. Equipment types.
7. Enrollments.
8. Examinations.
9. Examination requirements.
10. Room capacities.
11. Room equipment.
12. Room availability.
13. Invigilator availability.
14. Student accommodations.
15. Derived examination participation.

Parents must exist before children are generated.

### 9.5 Realistic distributions

Create meaningful distributions for:

- Enrollment counts.
- Room capacities.
- Equipment availability.
- Examination duration.
- Accommodation types.
- Invigilator availability.
- Room closures.
- Conflict degree.

Avoid creating a dataset in which every record has the same pattern.

Do not claim distributions are based on real institutional observations unless a lawful documented source supports that claim.

### 9.6 Derived values

Calculate from source records:

- Enrollment totals.
- Exam participation.
- Conflict counts.
- Room requirements.
- Invigilator requirements.
- Utilization.
- Scheduling outcomes.
- Status.

Do not independently randomize derived values.

### 9.7 Valid conflicts versus invalid conflicts

This is critical:

A student enrolled in two different courses that have examinations is a normal source-data situation.

This creates a conflict graph edge.

It is not itself an anomaly.

The violation occurs only when those two examinations are assigned overlapping intervals.

Keep this distinction throughout generation, validation and reporting.

### 9.8 Negative scenario fixtures

Create separate test fixtures for all five mandatory failures.

1. Student overlapping two examination assignments.
2. Room capacity exceeded.
3. Invigilator double-booked.
4. Applicable accommodation ignored.
5. Examination outside room availability.

Use valid baseline parent records wherever possible.

Do not contaminate valid baseline records.

### 9.9 Ground truth

Create separate files:

data/ground_truth/ground_truth.csv

data/ground_truth/ground_truth.json

Include:
- Scenario ID.
- Issue type.
- Affected record IDs.
- Expected result.
- Expected reason code.
- Scenario explanation.

Never load ground-truth labels as operational scheduler inputs.

The scheduler must derive the decision from source records and constraints.

### 9.10 Data exports

Create:

- CSV per entity.
- JSON per entity or documented collection.
- SQL seed data.
- Ground-truth files.
- README.
- Data dictionary.
- Source manifest.
- Validation report.

### 9.11 Reproducibility

Generate the complete dataset twice.

Sort records by primary ID before hashing.

Compare:
- Row counts.
- IDs.
- Foreign keys.
- Derived values.
- CSV hashes.
- JSON hashes.
- Ground-truth hashes.

Use SHA-256.

Keep current generation time out of canonical content hashes.

Produce a reproducibility report containing actual results.

==================================================
10. SCHEDULING ENGINE — COMPLETE BUSINESS LOGIC
==================================================

Implement a deterministic, explainable Python scheduling algorithm.

This product does not need an external optimization framework.

Use a most-constrained-first greedy algorithm with deterministic candidate scoring and a bounded improvement pass.

Be honest about the fact that greedy scheduling does not guarantee a mathematically optimal result.

### 10.1 Input preparation

For a scheduling run:

1. Load applicable examinations.
2. Load eligible students from enrollments.
3. Load examination requirements.
4. Load student accommodations.
5. Load rooms.
6. Load effective capacities.
7. Load equipment.
8. Load room availability.
9. Load invigilators.
10. Load availability.
11. Load applicable institutional configuration.

Validate source relationships before scheduling.

Do not proceed with unresolved invalid parent references.

### 10.2 Student examination durations

For each exam-student pair:

base_duration = examination duration requirement.

extra_duration = applicable accommodation adjustment.

effective_duration = base_duration + approved extra duration.

If percentage adjustments are approved, use the explicitly configured formula and deterministic rounding policy.

Record the actual calculated duration in the scheduling snapshot.

Do not change historical durations if the source accommodation later changes.

### 10.3 Conflict graph

Represent each examination as a node.

Create an edge when the examinations share at least one eligible student.

For each node calculate:

- Conflict degree.
- Shared enrollment counts.
- Eligible enrollment count.

Use a student-to-exam mapping to build the graph efficiently.

Do not repeatedly compare all exams against all students if a single-pass mapping works.

### 10.4 Exam ordering

Prioritize:

1. Highest conflict degree.
2. Largest enrollment.
3. Most restrictive requirement combination.
4. Fewest compatible rooms.
5. Stable examination ID.

Use a deterministic sort.

Store the priority explanation.

### 10.5 Candidate time generation

Generate available candidate start times from:

- Academic scheduling date range.
- Operating hours.
- Approved breaks.
- Slot granularity.
- Exam duration.
- Applicable restrictions.

Do not assume an exam must fit into a preselected arbitrary number of slots if it legitimately requires a longer continuous interval.

Use start-inclusive, end-exclusive interval logic.

### 10.6 Student conflict validation

For each student assigned to a candidate exam:

Check whether their effective examination interval overlaps another confirmed or candidate assignment in the same run.

Use:

overlap = candidate_start < existing_end AND existing_start < candidate_end

If overlap is true, reject the candidate.

The same student cannot receive two rooms for the same examination.

### 10.7 Candidate room discovery

For each candidate time:

Identify rooms satisfying:

- Available for the required interval.
- Not closed.
- Capacity record exists and is effective.
- Required equipment exists.
- Required room features exist.
- No conflicting room assignment exists.

Do not trust a room's display status as evidence of availability.

Evaluate the actual availability records.

### 10.8 Room allocation

One examination may require multiple rooms.

Implement a deterministic room-allocation algorithm.

Steps:

1. Prepare the eligible student list.
2. Calculate each student's room requirements.
3. Sort students by accommodation restrictiveness.
4. Sort compatible rooms by the chosen best-fit rule.
5. Allocate students while checking remaining seats.
6. Move to another compatible room when necessary.
7. Continue until every student has been allocated.
8. Verify every room independently.
9. Reject the entire candidate if any student remains unallocated.

Use a documented best-fit strategy.

Do not mark a partially allocated examination as scheduled.

### 10.9 Room occupation

A room remains allocated until the longest individual exam duration among its allocated students has elapsed.

Calculate room occupation from the students assigned to that room.

The room and its invigilators must remain reserved throughout that occupation interval.

This conservative policy must be documented as a configurable assumption.

### 10.10 Equipment and accommodation

A candidate room must satisfy every relevant mandatory requirement.

An examination may require equipment for every room.

A student may require specific room features.

The student must only be allocated to a room that satisfies their requirements.

If a valid allocation cannot be constructed, reject the entire exam-room allocation and record the affected requirement.

### 10.11 Invigilator staffing

Calculate required invigilators using the configured institutional ratio and any examination-specific policy.

Use a clearly labelled demo default until the institution's actual rule is known.

For every candidate invigilator check:

- Availability.
- Active status.
- Existing assignment overlap.
- Qualifications where applicable.
- Daily workload.
- Maximum approved workload.

Assign the required number for the entire room occupation interval.

Never assign one invigilator to overlapping duties.

### 10.12 Candidate validation

Create one central function:

validate_candidate()

Return a structured result:

- is_valid.
- passed_constraints.
- failed_constraints.
- reason_codes.
- resource_checks.
- student_checks.
- accommodation_checks.
- staffing_checks.

Do not combine candidate validation with candidate scoring.

Hard validation happens first.

### 10.13 Candidate scoring

Only valid candidates may be scored.

Use a deterministic score tuple.

Recommended priority:

1. Fewer rooms used.
2. Lower unused seat capacity.
3. Lower invigilator workload impact.
4. Better resource continuity.
5. Preferred time order.
6. Stable room identifier.

Document exactly how ties are broken.

Do not use arbitrary, undocumented weighted scores.

### 10.14 Commit decision

For each exam:

- Evaluate feasible candidate times.
- Evaluate valid room combinations.
- Evaluate invigilators.
- Select the best valid candidate.
- Persist the assignment.
- Persist student-room links.
- Persist invigilator links.
- Persist the decision.
- Persist an event.

Never persist a rejected candidate as a confirmed assignment.

### 10.15 Bounded improvement pass

After the first pass:

Revisit unassigned examinations.

Try alternative times and compatible resources.

Use deterministic bounded retries.

Do not silently displace another exam.

Any reassignment must be revalidated and recorded as a separate decision/event.

Do not allow an improvement pass to run indefinitely.

### 10.16 Reason codes

Support:

NO_ROOM_CAPACITY

ROOM_UNAVAILABLE

REQUIRED_EQUIPMENT_MISSING

ACCOMMODATION_UNSUPPORTED

NO_INVIGILATOR_AVAILABLE

NO_CONFLICT_FREE_TIME_SLOT

INSUFFICIENT_RESOURCE_CAPACITY

INVALID_SOURCE_DATA

Return multiple valid blocking reasons where appropriate.

Reason codes must come from actual candidate evaluations.

Do not label a scheduling timeout, missing configuration or lack of a tested candidate as proven global infeasibility.

### 10.17 Independent full-schedule validation

Create:

validate_complete_schedule()

This must independently reload stored assignments.

Verify:

- Student overlap.
- Student allocation completeness.
- Duplicate student allocation.
- Room capacity.
- Effective room capacity.
- Room availability.
- Room closure.
- Equipment.
- Accessibility.
- Extended duration.
- Invigilator availability.
- Invigilator overlap.
- Staffing requirements.
- Run consistency.
- Assignment lifecycle.
- Enrollment reconciliation.

Do not use the scheduler's success flag as proof.

If any confirmed hard-constraint violation exists:
- Block approval.
- Block publication.
- Create validation issues.
- Preserve diagnostic records.
- Make the failure visible.

### 10.18 Scheduling results

Every completed scheduling run must provide:

- Total exams.
- Scheduled exams.
- Unassigned exams.
- Scheduled students.
- Unscheduled students.
- Room assignments.
- Invigilator assignments.
- Candidate decisions.
- Failed checks.
- Reason codes.
- Validation results.
- Runtime.

All results must reconcile with actual database data.

==================================================
11. SCHEDULING RUN LIFECYCLE AND HISTORY
==================================================

Create a separate record for each scheduling run.

Record:

- Run ID.
- Academic period.
- Start time.
- Completion time.
- Algorithm version.
- Random seed if generation applies.
- Input snapshot hash.
- Settings snapshot.
- Exam count.
- Scheduled count.
- Unassigned count.
- Validation outcome.
- Status.

States:

DRAFT

VALIDATING

SCHEDULING

REVIEW_REQUIRED

APPROVED

PUBLISHED

FAILED

CANCELLED

SUPERSEDED

Define allowed state transitions.

An authorized academic administrator must approve and publish.

Do not automatically publish when the scheduler completes.

Preserve older schedules.

### History records

Maintain:

- SchedulingDecision.
- ScheduleEvent.
- AuditLog.
- ValidationIssue.

Do not overwrite important prior state.

Record actor, action, timestamp, previous state, new state and run reference.

Use appropriate database constraints and backend permissions to prevent normal users changing history.

==================================================
12. FASTAPI BACKEND CONTRACT
==================================================

Use a simple, understandable backend.

Folder structure:

backend/
    main.py
    config.py
    auth.py
    database.py

    routes/
        students.py
        courses.py
        enrollments.py
        exams.py
        rooms.py
        invigilators.py
        scheduling.py
        exceptions.py
        analytics.py
        audit.py

    services/
        student_service.py
        exam_service.py
        room_service.py
        scheduling_service.py
        report_service.py

    scheduler/
        conflict_graph.py
        candidate_generator.py
        room_allocator.py
        invigilator_allocator.py
        constraints.py
        scoring.py
        engine.py

    validation/
        data_validation.py
        schedule_validation.py

Separate API transport from business logic.

Do not put hundreds of lines of scheduling logic in one route function.

### API prefix

/api/v1

### Required endpoints

AUTHENTICATION AND PROFILE:

GET /api/v1/me

STUDENTS:

GET /api/v1/students

GET /api/v1/students/{student_id}

POST /api/v1/students

PATCH /api/v1/students/{student_id}

COURSES:

GET /api/v1/courses

POST /api/v1/courses

ENROLLMENTS:

GET /api/v1/enrollments

POST /api/v1/enrollments

EXAMINATIONS:

GET /api/v1/exams

GET /api/v1/exams/{exam_id}

POST /api/v1/exams

PATCH /api/v1/exams/{exam_id}

ROOMS:

GET /api/v1/rooms

GET /api/v1/rooms/{room_id}

POST /api/v1/rooms

PATCH /api/v1/rooms/{room_id}

INVIGILATORS:

GET /api/v1/invigilators

POST /api/v1/invigilators

ACCOMMODATIONS:

GET /api/v1/accommodations

POST /api/v1/accommodations

SCHEDULING:

POST /api/v1/scheduling/runs

GET /api/v1/scheduling/runs

GET /api/v1/scheduling/runs/{run_id}

GET /api/v1/scheduling/runs/{run_id}/assignments

GET /api/v1/scheduling/runs/{run_id}/decisions

POST /api/v1/scheduling/runs/{run_id}/validate

POST /api/v1/scheduling/runs/{run_id}/approve

POST /api/v1/scheduling/runs/{run_id}/publish

EXCEPTIONS:

GET /api/v1/exceptions

GET /api/v1/exceptions/{exception_id}

POST /api/v1/exceptions/{exception_id}/resolve

ANALYTICS:

GET /api/v1/analytics/overview

GET /api/v1/analytics/utilization

GET /api/v1/analytics/exceptions

AUDIT:

GET /api/v1/audit

Adapt endpoint details where required by the approved API contract.

Implement proper schemas, pagination, authorization and error responses.

### API reliability

- Do not trust client-provided roles.
- Validate all request values.
- Use transactions for important state changes.
- Prevent duplicate requests from producing duplicate assignments.
- Return correct HTTP status codes.
- Keep errors understandable but do not reveal secrets.
- Use consistent response formats.
- Document APIs through FastAPI OpenAPI.

### Execution mode

Benchmark the full 300-exam dataset.

Use synchronous scheduling initially if it completes reliably within the actual deployment request limits.

If not, implement a simple persisted job/status mechanism with a separate Render worker.

Do not introduce a distributed job framework.

Do not show fake progress indicators.

==================================================
13. SUPABASE INTEGRATION CONTRACT
==================================================

Use Supabase for PostgreSQL and authentication.

### Frontend integration

- Supabase Auth.
- Login.
- Logout.
- Session restoration.
- Access-token retrieval.
- Protected routes.

Use the Supabase JavaScript client.

Application business operations should normally go through FastAPI so business rules remain centralized.

### Backend integration

Use the Supabase Python SDK or its supported REST interface.

All protected endpoints must verify the user's actual access token.

Resolve the user identity from the verified token.

Resolve the user's actual role from a trusted source.

Do not accept a role from a request body.

For normal user-scoped access, prefer requests carrying the authenticated user's JWT so PostgreSQL RLS applies.

If privileged backend operations require a service-role key:

- Keep it on Render only.
- Validate the requesting user's permission before use.
- Use it only for a narrowly defined operation.
- Record the action in audit history.
- Never return it to the frontend.

### Database security

Implement RLS policies.

Test:
- Unauthenticated access.
- Learner access.
- Instructor access.
- Support staff access.
- Academic administrator access.
- Platform administrator access.
- Unauthorized data modifications.
- Cross-user reads.
- Sensitive accommodation access.

Do not call security complete until actual policy tests have been executed.

==================================================
14. ROLE-BASED FUNCTIONALITY
==================================================

Implement five roles.

LEARNER:
- View own profile.
- View own eligible examination timetable.
- View permitted examination details.
- View relevant notifications.

INSTRUCTOR:
- View permitted course records.
- View associated examinations.
- View published schedules.

ACADEMIC_ADMINISTRATOR:
- Manage examinations.
- Manage rooms.
- Manage invigilators.
- Run scheduling.
- Inspect decisions.
- Resolve exceptions.
- Approve and publish schedules.
- View analytics.

SUPPORT_STAFF:
- View permitted operational records.
- Manage assigned room/resource support workflows.
- View relevant accommodation requirements without unnecessary private details.

PLATFORM_ADMINISTRATOR:
- Manage users and approved roles.
- Manage institutional configuration.
- Manage authorized platform settings.

Define exact CRUD and action permissions in docs/permissions.md.

Do not create role capabilities merely for appearance.

==================================================
15. ANALYTICS AND METRIC DEFINITIONS
==================================================

All calculations must be traceable to database queries or documented backend aggregation.

### Scheduling completion

Fully scheduled eligible exams divided by total eligible exams, multiplied by 100.

Fully scheduled means every eligible student has a valid room assignment and all required resources are assigned.

### Student coverage

Scheduled eligible student-exam pairs divided by total eligible student-exam pairs, multiplied by 100.

### Room utilization

Reserved room-minutes divided by available room-minutes, multiplied by 100.

### Seat utilization

Assigned student-seat minutes divided by available capacity-seat minutes, multiplied by 100.

Define the calculation period precisely.

### Invigilator utilization

Assigned invigilator-minutes divided by available invigilator-minutes, multiplied by 100.

### Accommodation compliance

Satisfied applicable accommodation checks divided by all applicable accommodation checks, multiplied by 100.

### Exception counts

Aggregate actual validation and scheduling issues by:

- Reason code.
- Affected examination.
- Resource.
- Academic period.
- Resolution status.

Define behavior for zero denominators.

Distinguish:
- Draft.
- Published.
- Historical.

Avoid double counting the same examination across different scheduling runs.

==================================================
16. ERROR HANDLING AND AUDITABILITY
==================================================

Implement structured error handling.

Capture:
- User action.
- Resource.
- Operation.
- Result.
- Safe diagnostic information.

Do not log tokens, passwords, service keys or unnecessary sensitive student information.

Maintain event records for:

- Examination changes.
- Enrollment changes.
- Room changes.
- Availability changes.
- Accommodation changes.
- Scheduling runs.
- Assignment rejection.
- Assignment creation.
- Validation.
- Approval.
- Publication.
- Exception resolution.

Preserve previous state.

Use transaction boundaries for multi-record confirmation and publication.

A failed operation must not leave partially confirmed state.

==================================================
17. PERFORMANCE AND SCALE
==================================================

The primary workload is the required baseline dataset.

Optimize for:

- 5,000 students.
- 300 examinations.
- 100 rooms.
- 200 invigilators.

Use:
- Batch data generation.
- Batch database inserts.
- Pagination.
- Indexed lookups.
- Efficient dictionaries and sets.
- Efficient shared-enrollment aggregation.
- Cached conflict graph per input snapshot.
- Batched API responses.
- Proper database connection/client reuse.

Avoid:
- N+1 API requests.
- Repeated full-table requests.
- Rebuilding identical conflict data unnecessarily.
- Rendering thousands of table rows without pagination.
- Sending complete database datasets to the browser when unnecessary.

Benchmark actual full-scale execution.

Record:
- Data generation runtime.
- Database loading runtime.
- Scheduling runtime.
- Validation runtime.
- Major API response times.

Never invent performance claims.

==================================================
18. AUTOMATED TESTING CONTRACT
==================================================

Implement actual tests.

### Generator tests

- Exact baseline counts.
- Deterministic identifiers.
- Foreign-key consistency.
- Uniqueness.
- Allowed values.
- Derived values.
- Ground-truth separation.
- Reproducibility.

### Relationship tests

- Student-course enrollment.
- Course-exam association.
- Exam-requirement association.
- Room-capacity history.
- Room-equipment mapping.
- Invigilator availability.
- Student accommodation.
- Assignment-student relationships.
- Assignment-invigilator relationships.

### Scheduler tests

- Conflict graph.
- Time candidates.
- Student conflict.
- Room capacity.
- Room availability.
- Room closure.
- Equipment.
- Accommodation.
- Extended duration.
- Room splitting.
- Invigilator availability.
- Workload.
- Double-booking.
- Candidate scoring.
- Reason codes.
- Retry behavior.
- Schedule validation.

### Five required negative tests

TEST A:
Create an overlapping student examination candidate.

Expected:
- Detected.
- Rejected.
- Reason code generated.
- No invalid confirmed assignment.

TEST B:
Create a candidate that exceeds room capacity.

Expected:
- Detected.
- Rejected.
- NO_ROOM_CAPACITY or equivalent documented reason.

TEST C:
Double-book an invigilator.

Expected:
- Detected.
- Rejected.
- NO_INVIGILATOR_AVAILABLE or specific double-booking reason.

TEST D:
Ignore an applicable student accommodation.

Expected:
- Detected.
- Rejected.
- ACCOMMODATION_UNSUPPORTED.

TEST E:
Assign an examination outside the room's availability.

Expected:
- Detected.
- Rejected.
- ROOM_UNAVAILABLE.

For each test verify actual persisted state.

### Database tests

- RLS.
- Authorization.
- Foreign keys.
- Uniqueness.
- Constraints.
- Historical event preservation.
- Transaction behavior.

Prefer PostgreSQL/Supabase integration tests for PostgreSQL-specific behavior.

### API tests

- Authentication.
- Permissions.
- Valid requests.
- Invalid requests.
- Duplicate operations.
- Pagination.
- API error responses.
- Exports.

### Frontend tests

Test the most important user interactions and form validation.

### Reproducibility

Run the generator twice with the same seed and compare canonical checksums.

### Acceptance target

Confirmed hard-constraint violations: ZERO.

Every unassigned examination: reason-coded.

Every required negative scenario: detected.

All generated foreign keys: valid.

Ground truth: separate.

History: preserved.

Metrics: reconciled.

Generation: reproducible.

==================================================
19. DEMO EXPERIENCE
==================================================

Prepare a polished synthetic-data demonstration environment.

A technical reviewer should be able to:

1. Open the application.
2. Authenticate through the documented demo method.
3. Explore the overview.
4. Inspect examination records.
5. Browse rooms.
6. Browse invigilators.
7. Start a scheduling run.
8. View scheduled examinations.
9. Inspect why an examination was assigned.
10. Inspect an unassigned examination.
11. See the reason code.
12. Review validation results.
13. Inspect analytics.
14. Review audit history.

Use a safe reviewer/demo identity with explicit permissions.

Do not give an unrestricted public administrator account.

Keep synthetic data separate from real institutional data.

==================================================
20. REPOSITORY STRUCTURE
==================================================

Use a simple understandable monorepo.

examops/
│
├── AGENTS.md
├── README.md
├── .gitignore
├── .env.example
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── components/
│       ├── layouts/
│       ├── pages/
│       ├── context/
│       ├── hooks/
│       ├── services/
│       ├── utils/
│       └── styles/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── auth.py
│   ├── database.py
│   ├── routes/
│   ├── services/
│   ├── scheduler/
│   ├── validation/
│   └── requirements.txt
│
├── supabase/
│   └── migrations/
│
├── generator/
│   ├── generate.py
│   ├── config.py
│   ├── scenarios.py
│   ├── load_seed.py
│   └── validate.py
│
├── data/
│   ├── generated/
│   ├── ground_truth/
│   └── manifests/
│
├── tests/
│   ├── test_generator.py
│   ├── test_relationships.py
│   ├── test_constraints.py
│   ├── test_scheduler.py
│   ├── test_edge_cases.py
│   ├── test_api.py
│   └── test_reproducibility.py
│
└── docs/
    ├── source/
    ├── requirements.md
    ├── requirements_traceability.md
    ├── architecture.md
    ├── data_dictionary.md
    ├── erd.md
    ├── business_rules.md
    ├── permissions.md
    ├── scheduling_algorithm.md
    ├── API.md
    ├── security.md
    ├── design_system.md
    ├── testing.md
    ├── validation_report.md
    ├── source_manifest.md
    ├── assumptions.md
    ├── known_limitations.md
    ├── deployment.md
    ├── interview_guide.md
    └── ai_prompt_history.md

Adapt only with a documented reason.

==================================================
21. DOCUMENTATION DELIVERABLES
==================================================

Create professional documentation.

README:
- Product summary.
- Screenshots.
- Features.
- Technology stack.
- Architecture.
- Prerequisites.
- Installation.
- Environment setup.
- Supabase setup.
- Migrations.
- Data generation.
- Frontend execution.
- Backend execution.
- Tests.
- Deployment.
- Demo instructions.
- Known limitations.

Data dictionary:
- Every entity.
- Every field.
- Types.
- Relationships.
- Allowed values.
- Validation.
- Units.

Scheduling documentation:
- Conflict graph.
- Algorithm.
- Ordering.
- Candidate generation.
- Room allocation.
- Student allocation.
- Invigilator allocation.
- Constraints.
- Candidate scoring.
- Reason codes.
- Limitations.

Source manifest:
- Data source.
- Source URL where applicable.
- Version.
- Retrieval date.
- License.
- Transformations.
- Fields discarded.

For a wholly synthetic dataset, record that fact explicitly and document the generator seed and provenance.

Interview guide:
Explain the actual implementation in understandable language.

Provide:
- Concept.
- Explanation.
- Example.
- Relevant code file.
- Interview question.
- Correct answer.
- Trade-off.

Do not write theoretical explanations that contradict the actual implementation.

==================================================
22. AI PROMPT HISTORY AND RECRUITMENT COMPLIANCE
==================================================

Maintain docs/ai_prompt_history.md.

Record every prompt sent to AI tools used for this project, as required by the recruitment guidelines.

Record:
- Date.
- Tool.
- Actual prompt.
- Purpose.
- Files affected.
- Candidate review.
- Modifications.
- Verification performed.

If a tool does not expose previous prompts, document that limitation honestly.

The candidate must understand and take ownership of the implementation.

Do not falsely claim independent coding.

Prepare the repository for public GitHub submission.

Before publication:
- Scan for secrets.
- Inspect .env files.
- Inspect Git history for accidental secrets.
- Verify documentation.
- Verify licenses.
- Verify generated data is synthetic.

Use meaningful commits.

Never commit private credentials or actual student information.

Preserve the official 72-hour submission deadline.

==================================================
23. DEVELOPMENT EXECUTION STRATEGY
==================================================

Do not create the full project in one uncontrolled generation task.

Build in the following sequence.

PHASE 0 — SOURCE REQUIREMENTS AND DISCOVERY

Read all source documents.

Create:
- Requirements checklist.
- Business-rule register.
- Assumptions.
- Risk register.

PHASE 1 — DOMAIN AND DATABASE

Complete:
- Data dictionary.
- ER diagram.
- SQL migrations.
- Keys.
- Relationships.
- Constraints.
- RLS.

Verify with migrations and database tests.

PHASE 2 — SYNTHETIC DATA

Complete:
- Starter generator.
- Full generator.
- Ground truth.
- Five edge cases.
- Exports.
- Validation.
- Reproducibility.

PHASE 3 — SCHEDULING ALGORITHM

Complete:
- Conflict graph.
- Priority ordering.
- Candidate slots.
- Room allocation.
- Student allocation.
- Accommodations.
- Invigilators.
- Reason codes.
- Independent validator.

Test with small fixtures first, then the full baseline.

PHASE 4 — BACKEND

Complete:
- Authentication.
- Role verification.
- CRUD.
- Scheduling APIs.
- Audit.
- Exceptions.
- Analytics.
- Exports.

PHASE 5 — DESIGN SYSTEM

Complete:
- Brand.
- Typography.
- Tokens.
- Sidebar.
- Header.
- Tables.
- Forms.
- Drawers.
- Calendars.
- States.

PHASE 6 — APPLICATION

Implement and integrate all required modules.

PHASE 7 — QUALITY REVIEW

Run:
- Unit tests.
- Integration tests.
- Negative tests.
- Authentication tests.
- Full-scale generator tests.
- Reproducibility tests.
- End-to-end workflows.

PHASE 8 — DEPLOYMENT

Deploy:
- Vercel.
- Render.
- Supabase.

Verify the real deployed system.

PHASE 9 — FINAL AUDIT

Trace every original requirement to:
- Implemented code.
- Test.
- Evidence.
- Result.

Prepare the final public repository and submission documentation.

==================================================
24. IMPLEMENTATION RULES FOR ANTIGRAVITY
==================================================

At the start of each session:

1. Read this AGENTS.md.
2. Read the approved roadmap.
3. Inspect actual files.
4. Identify the current milestone.
5. Preserve stable functionality.

For every implementation task:

1. State the goal.
2. Inspect related code.
3. Define bounded changes.
4. Implement.
5. Run tests.
6. Inspect actual behavior.
7. Fix failures.
8. Update documentation.
9. Report remaining issues.

Avoid:
- Massive files.
- Duplicate functions.
- Placeholder logic.
- Hardcoded production metrics.
- Unused components.
- Unnecessary dependencies.
- Blind overwrites.
- Repeated requests for already supplied information.

Do not create separate competing versions of the same business rule in the frontend and backend.

The backend is authoritative for business decisions.

The database is authoritative for persisted state.

The frontend is responsible for presentation and user interaction.

==================================================
25. REQUIREMENTS TRACEABILITY AND FINAL ACCEPTANCE
==================================================

Create a traceability matrix.

Every original requirement must contain:

- ID.
- Original requirement.
- Implementation location.
- Database impact.
- API impact.
- UI impact.
- Test case.
- Verification evidence.
- Current status.

Statuses:

NOT_STARTED

IN_PROGRESS

IMPLEMENTED

VERIFIED

BLOCKED

Only VERIFIED means the implementation has objective test evidence.

### FINAL ACCEPTANCE GATE

DATA:
- All required baseline entity counts match.
- IDs are correct.
- Relationships are valid.
- Derived values reconcile.
- Ground truth is separate.
- Reproducibility passes.

SCHEDULING:
- Conflict graph is correct.
- Capacity is enforced.
- Availability is enforced.
- Equipment is enforced.
- Accommodations are enforced.
- Invigilator allocation is valid.
- No duplicate student-room allocation.
- Full schedule independently validates.
- Every unassigned exam has reasons.

DATABASE:
- Migrations work.
- Foreign keys work.
- RLS works.
- Historical runs remain preserved.

APPLICATION:
- Login works.
- Permissions work.
- CRUD works.
- Scheduling works.
- Exceptions work.
- Analytics work.
- Exports work.
- Audit works.

UI:
- All required modules exist.
- All critical interactions work.
- No dead buttons.
- No fake metrics.
- No broken responsive layouts.
- Loading/error/empty states exist.

SUBMISSION:
- README complete.
- Public GitHub repository.
- Meaningful commit history.
- AI prompt history.
- Validation report.
- Test evidence.
- Source manifest.
- Known limitations.
- Interview guide.

Do not report overall completion while any mandatory acceptance requirement is unverified.

==================================================
26. FIRST ACTION — DISCOVERY MODE
==================================================

Immediately inspect the project workspace.

Do not start application implementation yet.

Read the original source requirements and both recruitment PDFs.

Then create the discovery documents:

1. docs/source/requirements_original.md
2. docs/requirements.md
3. docs/requirements_traceability.md
4. docs/business_rules.md
5. docs/assumptions.md
6. docs/data_dictionary.md
7. docs/erd.md
8. docs/scheduling_algorithm.md
9. docs/architecture.md
10. docs/security.md
11. docs/design_system.md
12. docs/ui_ux_specification.md
13. docs/testing.md
14. docs/implementation_plan.md
15. docs/technical_risks.md

Produce Mermaid diagrams where helpful.

Show a worked three-examination scheduling example.

Show a worked room-splitting example with different student accommodation requirements.

Show how all five required negative scenarios will be detected.

Present unresolved decisions with recommended defaults.

Do not ask me to reconsider the stack.

Do not invent institution-specific policy.

Once critical decisions are approved, begin implementation one verified milestone at a time.

FINAL INSTRUCTION:

Build ExamOps as a complete, coherent enterprise product.

Do not optimize for impressive-looking generated source code.

Optimize for:
- Correctness.
- Usability.
- Reliability.
- Security.
- Explainability.
- Data integrity.
- Reproducibility.
- Traceability.
- Maintainability.
- Demonstrable engineering understanding.

The final application must be something an external technical evaluator can operate, inspect, challenge and independently verify.