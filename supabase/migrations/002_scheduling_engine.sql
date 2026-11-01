-- ==============================================================================
-- ExamOps PostgreSQL Migration: 002_scheduling_engine.sql
-- Description: Operational scheduling runs, frozen participant snapshots,
--              assignments, composite multi-room seating integrity, invigilators,
--              algorithmic decisions, diagnostic issues, events, and audit logs.
-- Entities Created: 9 of 26 (Total 26 of 26 entities now created)
-- ==============================================================================

-- ==============================================================================
-- 18. Scheduling Runs
-- ==============================================================================
CREATE TABLE IF NOT EXISTS scheduling_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_code VARCHAR(32) NOT NULL UNIQUE,
    academic_period_id UUID NOT NULL REFERENCES academic_periods(id) ON DELETE RESTRICT,
    created_by UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    algorithm_version VARCHAR(30) NOT NULL DEFAULT '1.0.0',
    seed BIGINT DEFAULT 20261022,
    input_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    input_snapshot_hash CHAR(64) NOT NULL,
    settings_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' 
        CHECK (status IN ('DRAFT', 'SCHEDULING', 'REVIEW_REQUIRED', 'APPROVED', 'PUBLISHED', 'CANCELLED', 'SUPERSEDED')),
    total_exams INTEGER NOT NULL DEFAULT 0 CHECK (total_exams >= 0),
    scheduled_count INTEGER NOT NULL DEFAULT 0 CHECK (scheduled_count >= 0 AND scheduled_count <= total_exams),
    unassigned_count INTEGER NOT NULL DEFAULT 0 CHECK (unassigned_count >= 0),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_run_code_format CHECK (run_code ~ '^RUN-[0-9]{8}-[0-9]{4}$')
);

CREATE INDEX IF NOT EXISTS idx_sr_period_id ON scheduling_runs(academic_period_id);
CREATE INDEX IF NOT EXISTS idx_sr_status ON scheduling_runs(status);
CREATE INDEX IF NOT EXISTS idx_sr_created_by ON scheduling_runs(created_by);

-- Partial Unique Index: Exactly one PUBLISHED schedule run per academic period
CREATE UNIQUE INDEX IF NOT EXISTS uq_published_run_per_period 
ON scheduling_runs(academic_period_id) 
WHERE (status = 'PUBLISHED');

-- ==============================================================================
-- 19. Schedule Assignments
-- ==============================================================================
CREATE TABLE IF NOT EXISTS schedule_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_code VARCHAR(64) NOT NULL,
    scheduling_run_id UUID NOT NULL REFERENCES scheduling_runs(id) ON DELETE RESTRICT,
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE RESTRICT,
    room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'CONFIRMED' 
        CHECK (status IN ('CONFIRMED', 'REJECTED', 'SUPERSEDED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_sa_times CHECK (end_time > start_time),
    CONSTRAINT uq_run_assignment_code UNIQUE (scheduling_run_id, assignment_code),
    CONSTRAINT uq_sa_composite UNIQUE (id, scheduling_run_id, exam_id, room_id)
);

CREATE INDEX IF NOT EXISTS idx_sa_run_id ON schedule_assignments(scheduling_run_id);
CREATE INDEX IF NOT EXISTS idx_sa_exam_id ON schedule_assignments(exam_id);
CREATE INDEX IF NOT EXISTS idx_sa_room_id ON schedule_assignments(room_id);
CREATE INDEX IF NOT EXISTS idx_sa_times ON schedule_assignments(start_time, end_time);

-- ==============================================================================
-- 20. Run Exam Students (Frozen Input Snapshot Table)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS run_exam_students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheduling_run_id UUID NOT NULL REFERENCES scheduling_runs(id) ON DELETE RESTRICT,
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE RESTRICT,
    base_duration_minutes INTEGER NOT NULL CHECK (base_duration_minutes > 0),
    extra_duration_minutes INTEGER NOT NULL DEFAULT 0 CHECK (extra_duration_minutes >= 0),
    effective_duration_minutes INTEGER NOT NULL CHECK (effective_duration_minutes >= base_duration_minutes),
    has_accommodation BOOLEAN NOT NULL DEFAULT FALSE,
    accommodation_details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_res_run_exam_student UNIQUE (scheduling_run_id, exam_id, student_id),
    CONSTRAINT uq_res_composite UNIQUE (id, scheduling_run_id, exam_id, student_id)
);

CREATE INDEX IF NOT EXISTS idx_res_run_id ON run_exam_students(scheduling_run_id);
CREATE INDEX IF NOT EXISTS idx_res_exam_id ON run_exam_students(exam_id);
CREATE INDEX IF NOT EXISTS idx_res_student_id ON run_exam_students(student_id);

-- ==============================================================================
-- 21. Assignment Students (Seating Bridge with Composite Integrity)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS assignment_students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES schedule_assignments(id) ON DELETE RESTRICT,
    run_exam_student_id UUID NOT NULL UNIQUE REFERENCES run_exam_students(id) ON DELETE RESTRICT,
    scheduling_run_id UUID NOT NULL REFERENCES scheduling_runs(id) ON DELETE RESTRICT,
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE RESTRICT,
    room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    effective_duration_minutes INTEGER NOT NULL CHECK (effective_duration_minutes > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_asgn_student UNIQUE (assignment_id, student_id),
    -- Composite FK 1: Guarantees assignment, run, exam, and room match exactly
    CONSTRAINT fk_asgn_sa_composite FOREIGN KEY (assignment_id, scheduling_run_id, exam_id, room_id)
        REFERENCES schedule_assignments(id, scheduling_run_id, exam_id, room_id) ON DELETE RESTRICT,
    -- Composite FK 2: Guarantees snapshot, run, exam, and student match exactly
    CONSTRAINT fk_asgn_res_composite FOREIGN KEY (run_exam_student_id, scheduling_run_id, exam_id, student_id)
        REFERENCES run_exam_students(id, scheduling_run_id, exam_id, student_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_as_assignment_id ON assignment_students(assignment_id);
CREATE INDEX IF NOT EXISTS idx_as_student_id ON assignment_students(student_id);
CREATE INDEX IF NOT EXISTS idx_as_res_id ON assignment_students(run_exam_student_id);

-- ==============================================================================
-- 22. Assignment Invigilators
-- ==============================================================================
CREATE TABLE IF NOT EXISTS assignment_invigilators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES schedule_assignments(id) ON DELETE RESTRICT,
    invigilator_id UUID NOT NULL REFERENCES invigilators(id) ON DELETE RESTRICT,
    role VARCHAR(20) NOT NULL DEFAULT 'PRIMARY' 
        CHECK (role IN ('PRIMARY', 'SECONDARY', 'RELIEF')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_asgn_inv UNIQUE (assignment_id, invigilator_id)
);

CREATE INDEX IF NOT EXISTS idx_ai_assignment_id ON assignment_invigilators(assignment_id);
CREATE INDEX IF NOT EXISTS idx_ai_invigilator_id ON assignment_invigilators(invigilator_id);

-- ==============================================================================
-- 23. Scheduling Decisions (Full Algorithm Telemetry)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS scheduling_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheduling_run_id UUID NOT NULL REFERENCES scheduling_runs(id) ON DELETE RESTRICT,
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE RESTRICT,
    decision_order INTEGER NOT NULL CHECK (decision_order >= 0),
    is_assigned BOOLEAN NOT NULL,
    reason_codes TEXT[] NOT NULL DEFAULT '{}',
    selected_candidate JSONB,
    candidate_details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_sd_run_exam UNIQUE (scheduling_run_id, exam_id)
);

CREATE INDEX IF NOT EXISTS idx_sd_run_id ON scheduling_decisions(scheduling_run_id);
CREATE INDEX IF NOT EXISTS idx_sd_exam_id ON scheduling_decisions(exam_id);
CREATE INDEX IF NOT EXISTS idx_sd_is_assigned ON scheduling_decisions(is_assigned);

-- ==============================================================================
-- 24. Schedule Events (State Change Trail)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS schedule_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheduling_run_id UUID NOT NULL REFERENCES scheduling_runs(id) ON DELETE RESTRICT,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_se_run_id ON schedule_events(scheduling_run_id);
CREATE INDEX IF NOT EXISTS idx_se_entity ON schedule_events(entity_type, entity_id);

-- ==============================================================================
-- 25. Validation Issues (Diagnostic Exceptions)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS validation_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheduling_run_id UUID NOT NULL REFERENCES scheduling_runs(id) ON DELETE RESTRICT,
    exam_id UUID REFERENCES exams(id) ON DELETE RESTRICT,
    assignment_id UUID REFERENCES schedule_assignments(id) ON DELETE RESTRICT,
    issue_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'CRITICAL' 
        CHECK (severity IN ('CRITICAL', 'WARNING', 'INFO')),
    description TEXT NOT NULL,
    resolution_status VARCHAR(20) NOT NULL DEFAULT 'OPEN' 
        CHECK (resolution_status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED', 'WONT_FIX')),
    resolved_by UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vi_run_id ON validation_issues(scheduling_run_id);
CREATE INDEX IF NOT EXISTS idx_vi_severity ON validation_issues(severity);
CREATE INDEX IF NOT EXISTS idx_vi_status ON validation_issues(resolution_status);

-- ==============================================================================
-- 26. Audit Logs (Append-Only Non-Repudiable Log)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    user_role VARCHAR(30),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    result VARCHAR(20) NOT NULL DEFAULT 'SUCCESS' 
        CHECK (result IN ('SUCCESS', 'FAILURE', 'DENIED')),
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_al_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_al_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_al_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_al_created_at ON audit_logs(created_at);

-- ==============================================================================
-- Immutability Triggers for Append-Only Operational Logs
-- ==============================================================================
CREATE OR REPLACE FUNCTION public.prevent_modification_of_immutable_logs()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Disallowed: table % is append-only and cannot be updated or deleted.', TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_logs_immutable ON audit_logs;
CREATE TRIGGER trg_audit_logs_immutable
BEFORE UPDATE OR DELETE ON audit_logs
FOR EACH ROW EXECUTE FUNCTION public.prevent_modification_of_immutable_logs();

DROP TRIGGER IF EXISTS trg_decisions_immutable ON scheduling_decisions;
CREATE TRIGGER trg_decisions_immutable
BEFORE UPDATE OR DELETE ON scheduling_decisions
FOR EACH ROW EXECUTE FUNCTION public.prevent_modification_of_immutable_logs();

DROP TRIGGER IF EXISTS trg_events_immutable ON schedule_events;
CREATE TRIGGER trg_events_immutable
BEFORE UPDATE OR DELETE ON schedule_events
FOR EACH ROW EXECUTE FUNCTION public.prevent_modification_of_immutable_logs();

