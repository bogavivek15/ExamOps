# ExamOps — AI Prompt History & Transparent LLM Usage Log

> **Recruitment Drive:** YottaFlex AI Candidate Project  
> **Compliance Pillar:** "Use LLMs Transparently — Prompt History Required" (Submission Guidelines §03)  
> **Authoritative Sources:** `candidate_faq.pdf` Q6, `submission_guidelines.pdf` Pillar 03  
> **Last Updated:** 2026-11-03  

---

## 1. Compliance & Transparency Disclosure

In full adherence to the YottaFlex AI Candidate Project Submission Guidelines:
- All prompts submitted to AI assistants throughout this project are logged in chronological order below and archived in full text under [`docs/ai_prompts/`](ai_prompts/).
- **Autonomous Multi-Phase Execution Disclosure (FAQ Q6 Compliance):**  
  Following initial discovery mode (Prompts 001–003), the candidate issued Prompt 004 authorizing an autonomous multi-phase engineering autopilot within Google Antigravity. Individual micro-actions and tool calls were directed autonomously by the agent to implement Phases 1 through 11. Complete phase execution telemetry, defect registers, and architectural decisions are preserved in `docs/architecture.md`, `docs/validation_report.md`, and `docs/evaluation.md`.
- No separate unrecorded external LLMs (such as independent ChatGPT conversations) were used for implementation. All AI interactions occurred via Google Antigravity.
- The candidate understands, owns, and has independently verified the architectural decisions, code contracts, mathematical algorithms, and testing suites.

---

## 2. Chronological Prompt Ledger

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
