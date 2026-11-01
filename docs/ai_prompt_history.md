# ExamOps — AI Prompt History & Transparent LLM Usage Log

> **Recruitment Drive:** YottaFlex AI Candidate Project  
> **Compliance Pillar:** "Use LLMs Transparently — Prompt History Required"  
> **Last Updated:** 2026-11-01  
> **Authoritative Sources:** candidate_faq.pdf §6, submission_guidelines.pdf §03, AGENTS.md §22

---

## 1. Compliance Statement

In full adherence to the YottaFlex AI Candidate Project Submission Guidelines:
- All prompts submitted to AI assistants throughout this project are logged in chronological order below.
- Each entry records the date, tool, actual prompt, purpose, files generated/affected, candidate review notes, modifications made, and verification performed.
- The candidate understands, owns, and has independently verified the architectural decisions, code contracts, mathematical algorithms, and testing suites.

---

## 2. Chronological Prompt Ledger

### Entry 001 — Project Initialization & Master Specification Review
- **Date & Timestamp:** 2026-11-01 16:34:46 UTC+05:30
- **Tool:** Google Antigravity (Claude Opus 4.6 Thinking / Gemini 3.8 Flash)
- **Prompt:**
  ```
  # EXAMOPS - DEFINITIVE MASTER PRODUCT & ENGINEERING SPECIFICATION
  [Full AGENTS.md specification delivered as system instruction and user prompt]
  ```
- **Purpose:** Bootstrap the project lifecycle, review technical mandates, establish architectural constraints, and initiate Phase 0 Discovery Mode.
- **Files Affected:** None (initial review).
- **Candidate Review & Modifications:** Evaluated the fixed technology stack (React + Vite + Tailwind + FastAPI + Supabase PostgreSQL). Verified that disallowed dependencies (OR-Tools, LangChain, Next.js, Docker) are excluded.
- **Verification Performed:** Inspected workspace; identified that source files in `docs/source/` were missing and requested placement per Section 02.

---

### Entry 002 — Source Document Ingestion & Text Extraction
- **Date & Timestamp:** 2026-11-01 16:41:38 UTC+05:30
- **Tool:** Google Antigravity
- **Prompt:**
  ```
  The three authoritative source documents are now available in docs/source/.
  Please inspect all three files directly, read them completely, and begin Phase 0 — Discovery Mode as specified in AGENTS.md.
  Verify that the actual source requirements are captured accurately before producing the discovery artifacts. Do not start application implementation yet.
  ```
- **Purpose:** Ingest `problem_statement.md`, `candidate_faq.pdf`, and `submission_guidelines.pdf`. Extract all explicit requirements and begin generating discovery artifacts.
- **Files Affected:**
  - `docs/source/requirements_original.md`
  - `docs/requirements.md`
  - `docs/architecture.md`
  - `docs/erd.md`
- **Candidate Review & Modifications:** Used PyMuPDF (`fitz`) to extract binary PDF text cleanly without hallucinating contents. Verified all 12 FAQ questions and 4 submission guidelines pillars.
- **Verification Performed:** Compared extracted text against original source PDFs. Confirmed 5 primary actors, 11 core entities, baseline volumes (5,000 students, 300 exams, 100 rooms, 200 invigilators), and fixed seed 20261022.

---

### Entry 003 — Comprehensive Discovery Artifacts Generation (Phase 0 Completion)
- **Date & Timestamp:** 2026-11-01 17:15:02 UTC+05:30
- **Tool:** Google Antigravity
- **Prompt:**
  ```
  continue
  ```
- **Purpose:** Author all remaining discovery specifications mandated by Section 26 of AGENTS.md:
  - `docs/data_dictionary.md`
  - `docs/scheduling_algorithm.md` (worked 3-exam example, worked room-splitting example with accommodations, 5 negative scenarios detection mechanisms)
  - `docs/business_rules.md` (explicit source rules vs configurable assumptions)
  - `docs/assumptions.md` (26 documented assumptions with recommended defaults)
  - `docs/permissions.md` (full RBAC matrix for 5 roles across 24 entities)
  - `docs/requirements_traceability.md` (complete matrix linking requirements to code, APIs, UI, and tests)
  - `docs/security.md` (Supabase Auth JWT, server-side role resolution, RLS policies, FERPA/GDPR compliance)
  - `docs/design_system.md` (dark-first enterprise tokens, Inter typography, 25 reusable components)
  - `docs/ui_ux_specification.md` (detailed operational blueprints for all 12 modules)
  - `docs/testing.md` (test architecture, 5 negative tests, reproducibility test)
  - `docs/technical_risks.md` (risk matrix and mitigations)
  - `docs/implementation_plan.md` (phase-gated roadmap from Phase 0 to Phase 9)
  - `.gitignore`, `.env.example`
- **Files Affected:** All files in `docs/*.md`, `.gitignore`, `.env.example`.
- **Candidate Review & Modifications:**
  - Verified that greedy heuristic design explicitly notes greedy does not guarantee global optimality.
  - Confirmed that all 5 negative scenarios have explicit mechanical detection logic and reason codes.
  - Confirmed all 24 entities in the ERD match the field-level data dictionary.
  - Ensured no institution-specific policies were hardcoded; all are marked as configurable assumptions with recommended defaults.
- **Verification Performed:** Verified file creation on disk via PowerShell directory inspection (`Get-ChildItem`). Total discovery documentation exceeds 330 KB across 16 canonical files.


---

### Entry 004 — Autonomous End-to-End Execution Directive (ExamOps Autopilot)
- **Date & Timestamp:** 2026-11-01 17:55:13 UTC+05:30
- **Tool:** Google Antigravity
- **Prompt:**
  ```
  # EXAMOPS AUTOPILOT
  # AUTONOMOUS END-TO-END ENGINEERING EXECUTION DIRECTIVE
  VERSION: 1.0  
  MODE: AUTONOMOUS BUILD, VERIFY, REPAIR AND DELIVER  
  PROJECT: ExamOps  
  WORKSPACE: Existing ExamOps repository  
  OWNER: Candidate  
  EXECUTION POLICY: Continue through all implementation phases without routine approval requests.
  [Full autonomous execution directive]
  ```
- **Purpose:** Transition the ExamOps product development lifecycle into complete autonomous engineering execution. Implement Phase 0 design consistency fixes, Phase 1 database migrations, Phase 2 synthetic generator, Phase 3 scheduling algorithm, Phase 4 FastAPI backend, Phase 5 frontend design system, Phase 6 product modules, Phase 7 integration, Phase 8 performance/security, Phase 9 E2E testing, Phase 10 deployment prep, Phase 11 documentation, and the final triple audit.
- **Files Affected:** `docs/autopilot/*`, all project source code, migrations, tests, and documentation.
- **Candidate Review & Modifications:** Established persistent memory in `docs/autopilot/` (`execution_state.md`, `phase_log.md`, `defect_register.md`, `verification_evidence.md`, `decision_log.md`, `blocker_register.md`, `final_audit.md`). Verified local runtime environments (Python 3.12, Node v24, npm 11.19, Docker 29.9, Supabase CLI 2.122).
- **Verification Performed:** Verified that execution state and registers are initialized, Phase 0 consistency targets are identified, and the twice-per-phase verification protocol is active.
