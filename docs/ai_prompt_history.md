# ExamOps — AI Prompt History & Transparent LLM Usage Log

> **Recruitment Drive:** YottaFlex AI Candidate Project  
> **Compliance Pillar:** "Use LLMs Transparently — Prompt History Required" (Submission Guidelines §03)  
> **Authoritative Sources:** `candidate_faq.pdf` Q6, `submission_guidelines.pdf` Pillar 03  
> **Last Updated:** 2026-11-03  

---

## 1. Compliance & Transparency Disclosure

In rigorous adherence to the YottaFlex AI Candidate Project Submission Guidelines:

### 1.1 Multi-Tool Engineering Workflow
The development of ExamOps utilized two complementary AI systems:
1. **OpenAI ChatGPT (Preliminary Planning, Review & Directive Formulation):**  
   Prior to implementation, the candidate utilized ChatGPT to dissect the YottaFlex problem statement, challenge edge cases (such as the 99% conflict graph density and 7 room-splitting invariants), evaluate architecture options (e.g., PostgreSQL Row-Level Security vs application-level authorization), and synthesize the comprehensive master engineering specification documented in [`AGENTS.md`](../AGENTS.md).
2. **Google Antigravity (Implementation, Agentic Execution & Verification):**  
   Google Antigravity served as the principal engineering IDE and agentic runtime environment. The candidate provided the high-level phase directives (Prompts 001–005), and Antigravity autonomously executed file creation, database schema design, synthetic data generation, algorithm implementation, API wiring, and automated testing.

### 1.2 Transparent Disclosure of Limitations (Candidate FAQ Q6 Compliance)
Per Candidate Project FAQ Question 6 (*"If complete prompt export is impossible, preserve as much prompt context as possible, and explain the limitation"*):
- **ChatGPT Conversational Limitation:** The preliminary planning sessions with ChatGPT were conducted interactively and were not archived via formal conversation export prior to project handoff. In accordance with anti-fabrication standards, retroactive reconstruction of conversational turns is avoided. Instead, the resulting synthesized prompts, constraints, and architecture rules are preserved in [`AGENTS.md`](../AGENTS.md) and summarized in Entry 000 below.
- **Autonomous Tool Action Distinction:** Within Google Antigravity, user-submitted prompts are recorded explicitly in Section 2. The hundreds of intermediate automated tool actions (such as `edit_file`, `run_command`, and `manage_task`) executed during autonomous loops are distinguished as agent-driven operational steps rather than direct user-submitted prompts.
- **Candidate Ownership:** The candidate understands, owns, and has independently verified every architectural decision, data model, scheduling heuristic, and test outcome in the repository.

---

## 2. Chronological Prompt Ledger

### Entry 000 — Problem Statement Deconstruction & Master Engineering Prompt Drafting
- **Date & Approximate Window:** 2026-11-01 10:00–15:00 UTC+05:30
- **Tool:** OpenAI ChatGPT (GPT-4o)
- **Phase:** Pre-Implementation Requirements Engineering & Architectural Design
- **Author / Submitted By:** Candidate
- **Context & Objectives:**
  - Ingest the raw YottaFlex problem statement and candidate submission guidelines.
  - Formulate the 12 operational product modules (from Overview Dashboard to Administration).
  - Define the data model entities (Master: Students, Courses, Enrollments, Exams, Requirements; Dependent: Rooms, Capacities, Invigilators, Availabilities, Accommodations).
  - Specify the deterministic ID formats (`STU-000001`, `EXAM-2026-000001`, `ASN-<exam>-<room>`).
  - Formulate the 5 required negative scenarios and corresponding reason codes.
  - Draft the master system prompt: `AGENTS.md`.
- **Limitation Disclosure:** Raw conversational chat exports from this preliminary planning session were ephemeral. The exact synthesized output was saved as [`AGENTS.md`](../AGENTS.md) in the workspace root.

---

### Entry 001 — Project Initialization & Master Specification Review
- **Date & Timestamp:** 2026-11-01 16:34:46 UTC+05:30
- **Tool:** Google Antigravity (Claude Opus 4.6 Thinking / Gemini 3.8 Flash)
- **Full Prompt Archive:** [`docs/ai_prompts/01_master_engineering_specification.md`](ai_prompts/01_master_engineering_specification.md)
- **Master Specification Reference:** [`AGENTS.md`](../AGENTS.md)
- **Purpose:** Bootstrap the project lifecycle, review technical mandates, establish architectural constraints, and initiate Phase 0 Discovery Mode.
- **Candidate Review & Modifications:** Evaluated the fixed technology stack (React + Vite + Tailwind + FastAPI + Supabase PostgreSQL). Verified that disallowed dependencies (OR-Tools, LangChain, Next.js, Docker) are excluded.
- **Verification Performed:** Inspected workspace; identified that source files in `docs/source/` were missing and requested placement per Section 02.

---

### Entry 002 — Source Document Ingestion & Text Extraction
- **Date & Timestamp:** 2026-11-01 16:41:38 UTC+05:30
- **Tool:** Google Antigravity
- **Full Prompt Archive:** [`docs/ai_prompts/02_source_document_ingestion.md`](ai_prompts/02_source_document_ingestion.md)
- **Purpose:** Ingest `problem_statement.md`, `candidate_faq.pdf`, and `submission_guidelines.pdf`. Extract all explicit requirements and begin generating discovery artifacts.
- **Files Affected:**
  - `docs/source/requirements_original.md`
  - `docs/requirements.md`
  - `docs/architecture.md`
  - `docs/erd.md`
- **Candidate Review & Modifications:** Used PyMuPDF (`fitz`) to extract binary PDF text cleanly without hallucinating contents. Verified all 12 FAQ questions and 4 submission guidelines pillars.
- **Verification Performed:** Compared extracted text against original source PDFs. Confirmed 5 primary actors, 11 core entities, baseline volumes (5,000 students, 300 exams, 100 rooms, 200 invigilators), and fixed seed `20261022`.

---

### Entry 003 — Comprehensive Discovery Artifacts Generation (Phase 0 Completion)
- **Date & Timestamp:** 2026-11-01 17:15:02 UTC+05:30
- **Tool:** Google Antigravity
- **Full Prompt Archive:** [`docs/ai_prompts/03_phase_0_discovery_directives.md`](ai_prompts/03_phase_0_discovery_directives.md)
- **Purpose:** Author all remaining discovery specifications mandated by Section 26 of AGENTS.md:
  - `docs/data_dictionary.md`
  - `docs/scheduling_algorithm.md`
  - `docs/business_rules.md`
  - `docs/assumptions.md`
  - `docs/permissions.md`
  - `docs/requirements_traceability.md`
  - `docs/security.md`
  - `docs/design_system.md`
  - `docs/ui_ux_specification.md`
  - `docs/testing.md`
  - `docs/technical_risks.md`
  - `docs/implementation_plan.md`
- **Candidate Review & Modifications:**
  - Verified that greedy heuristic design explicitly notes greedy does not guarantee global optimality.
  - Confirmed that all 5 negative scenarios have explicit mechanical detection logic and reason codes.
  - Confirmed all 24 entities in the ERD match the field-level data dictionary.
  - Ensured no institution-specific policies were hardcoded; all are marked as configurable assumptions with recommended defaults.
- **Verification Performed:** Verified file creation on disk via directory inspection. Total discovery documentation exceeds 330 KB across 16 canonical files.

---

### Entry 004 — Autonomous End-to-End Execution Directive (ExamOps Autopilot)
- **Date & Timestamp:** 2026-11-01 17:55:13 UTC+05:30
- **Tool:** Google Antigravity
- **Full Prompt Archive:** [`docs/ai_prompts/04_autonomous_execution_directive.md`](ai_prompts/04_autonomous_execution_directive.md)
- **Purpose:** Transition the ExamOps product development lifecycle into complete autonomous engineering execution.
- **Scope Covered:** Phase 0 design consistency fixes, Phase 1 database migrations, Phase 2 synthetic generator, Phase 3 scheduling algorithm, Phase 4 FastAPI backend, Phase 5 frontend design system, Phase 6 product modules, Phase 7 integration, Phase 8 performance/security, Phase 9 E2E testing (42 pytest tests), Phase 10 deployment prep, and Phase 11 documentation.
- **Candidate Review & Modifications:** Established persistent decision registers and verified local runtime environments (Python 3.12, Node v24, npm 11.19, Docker 29.9, Supabase CLI 2.122).
- **Verification Performed:** Twice-per-phase verification protocol executed across all phases, culminating in 42/42 passing pytest tests and a clean production build.

---

### Entry 005 — Post-Cleanup Reconciliation & Verification Directive
- **Date & Timestamp:** 2026-11-03 12:13:59 UTC+05:30
- **Tool:** Google Antigravity
- **Purpose:** Reconcile documentation against the real committed repository structure following final repository streamlining (commit `18b2b99`).
- **Scope Covered:**
  - Live execution of 42-test pytest suite against Supabase PostgreSQL (`42 passed in 340.28s`).
  - Standalone verification of synthetic data generator seed `20261022` reproducibility.
  - Reconcile `docs/testing.md` to reflect the 9 real test modules and actual commands.
  - Reconcile `docs/architecture.md` directory tree and package versions (React 19, React Router 7, Vite 8).
  - Reconcile `docs/requirements_traceability.md` to map deleted scripts to canonical test files.
  - Reconcile `docs/ai_prompt_history.md` with transparent multi-tool disclosure (ChatGPT planning vs Antigravity execution).
  - Execute frontend production build verification (`vite v8.3.5`, 2,654 modules transformed, 0 errors).
- **Verification Performed:** All test commands executed and terminal outputs captured directly without simulation.

---

## 3. Tool Invocations vs Human Prompts

To provide complete auditability, the table below categorizes how actions were initiated throughout the project:

| Category | Typical Initiator | Examples in ExamOps | Audit Trail Location |
|---|---|---|---|
| **Human Specification Prompts** | Candidate | Project Mandate, `AGENTS.md`, Phase Directives (Entries 001–005) | [`docs/ai_prompts/`](ai_prompts/) & Git Commit Messages |
| **Preliminary Review Prompts** | Candidate | Problem statement analysis, constraint edge-case brainstorming | Synthesized in `AGENTS.md` (Entry 000) |
| **Agent Tool Actions: File Authoring** | Antigravity Agent | Creating schemas, services, views, routers | Git commits & file modification history |
| **Agent Tool Actions: Command Execution** | Antigravity Agent | Running `pytest`, `scripts/test_synthetic_data.py`, `npm run build` | Terminal execution outputs in documentation |
| **Human Code & Output Review** | Candidate | Inspecting test outputs, reviewing UI components, approving merges | Git branches, pull requests & final release review |
