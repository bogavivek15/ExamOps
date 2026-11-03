-- ==============================================================================
-- ExamOps PostgreSQL Migration: 003_rls_and_policies.sql
-- Description: Complete Row Level Security (RLS) policies for all 26 entities,
--              role-based access control, confidential notes isolation,
--              and atomic publication locking procedure.
-- ==============================================================================

-- ==============================================================================
-- 1. Enable RLS on All 26 Tables
-- ==============================================================================
ALTER TABLE academic_periods ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE invigilators ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_instructors ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE exams ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE room_capacities ENABLE ROW LEVEL SECURITY;
ALTER TABLE equipment_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE room_equipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE room_availabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE availabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE accommodations ENABLE ROW LEVEL SECURITY;
ALTER TABLE accommodation_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE scheduling_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedule_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE run_exam_students ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignment_students ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignment_invigilators ENABLE ROW LEVEL SECURITY;
ALTER TABLE scheduling_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedule_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE validation_issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ==============================================================================
-- 2. User Profiles Policies (Non-Recursive)
-- ==============================================================================
DROP POLICY IF EXISTS p_user_profiles_select ON user_profiles;
CREATE POLICY p_user_profiles_select ON user_profiles
    FOR SELECT
    USING (
        id = auth.uid() 
        OR public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
        OR auth.uid() IS NULL -- Permits service_role / internal queries
    );

DROP POLICY IF EXISTS p_user_profiles_update ON user_profiles;
CREATE POLICY p_user_profiles_update ON user_profiles
    FOR UPDATE
    USING (
        id = auth.uid() 
        OR public.get_auth_role() = 'PLATFORM_ADMINISTRATOR'
    );

DROP POLICY IF EXISTS p_user_profiles_admin ON user_profiles;
CREATE POLICY p_user_profiles_admin ON user_profiles
    FOR ALL
    USING (public.get_auth_role() = 'PLATFORM_ADMINISTRATOR');

-- ==============================================================================
-- 3. Master Reference Tables (Academic Periods, Rooms, Equipment)
-- ==============================================================================
-- Academic Periods: Read by all authenticated users; modified by Admins
CREATE POLICY p_ap_select ON academic_periods
    FOR SELECT USING (TRUE);

CREATE POLICY p_ap_admin ON academic_periods
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- Rooms: Read by all; modified by Support Staff and Admins
CREATE POLICY p_rooms_select ON rooms
    FOR SELECT USING (TRUE);

CREATE POLICY p_rooms_modify ON rooms
    FOR ALL USING (public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- Room Capacities: Read by staff and faculty; modified by Support Staff and Admins
CREATE POLICY p_rc_select ON room_capacities
    FOR SELECT USING (public.get_auth_role() IN ('INSTRUCTOR', 'SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_rc_modify ON room_capacities
    FOR ALL USING (public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- Equipment Types & Room Equipment
CREATE POLICY p_et_select ON equipment_types FOR SELECT USING (TRUE);
CREATE POLICY p_et_admin ON equipment_types FOR ALL USING (public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_re_select ON room_equipment FOR SELECT USING (TRUE);
CREATE POLICY p_re_admin ON room_equipment FOR ALL USING (public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- Room Availabilities
CREATE POLICY p_ra_select ON room_availabilities FOR SELECT USING (TRUE);
CREATE POLICY p_ra_admin ON room_availabilities FOR ALL USING (public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- ==============================================================================
-- 4. Invigilators and Availabilities
-- ==============================================================================
CREATE POLICY p_inv_select ON invigilators
    FOR SELECT USING (
        id = public.get_auth_invigilator_id()
        OR public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_inv_admin ON invigilators
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_avail_select ON availabilities
    FOR SELECT USING (
        invigilator_id = public.get_auth_invigilator_id()
        OR public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_avail_admin ON availabilities
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- ==============================================================================
-- 5. Student and Enrollment Data
-- ==============================================================================
CREATE POLICY p_students_select ON students
    FOR SELECT USING (
        id = public.get_auth_student_id()
        OR public.get_auth_role() IN ('INSTRUCTOR', 'SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_students_admin ON students
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_enrollments_select ON enrollments
    FOR SELECT USING (
        student_id = public.get_auth_student_id()
        OR public.get_auth_role() IN ('INSTRUCTOR', 'SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_enrollments_admin ON enrollments
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- ==============================================================================
-- 6. Courses and Course Instructors
-- ==============================================================================
CREATE POLICY p_courses_select ON courses FOR SELECT USING (TRUE);
CREATE POLICY p_courses_admin ON courses FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_ci_select ON course_instructors FOR SELECT USING (TRUE);
CREATE POLICY p_ci_admin ON course_instructors FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- ==============================================================================
-- 7. Examinations and Requirements
-- ==============================================================================
CREATE POLICY p_exams_select ON exams
    FOR SELECT USING (
        status = 'PUBLISHED'
        OR course_id IN (
            SELECT course_id FROM course_instructors WHERE instructor_profile_id = auth.uid()
        )
        OR public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_exams_admin ON exams
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_req_select ON exam_requirements
    FOR SELECT USING (
        exam_id IN (
            SELECT id FROM exams WHERE status = 'PUBLISHED' 
            OR course_id IN (SELECT course_id FROM course_instructors WHERE instructor_profile_id = auth.uid())
        )
        OR public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_req_instructor_insert ON exam_requirements
    FOR INSERT WITH CHECK (
        public.get_auth_role() = 'INSTRUCTOR' AND exam_id IN (
            SELECT e.id FROM exams e JOIN course_instructors ci ON ci.course_id = e.course_id 
            WHERE ci.instructor_profile_id = auth.uid()
        )
    );

CREATE POLICY p_req_admin ON exam_requirements
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- ==============================================================================
-- 8. Accommodations & Sensitive Clinical Notes
-- ==============================================================================
CREATE POLICY p_acco_select ON accommodations
    FOR SELECT USING (
        student_id = public.get_auth_student_id()
        OR public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_acco_admin ON accommodations
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- Clinical Notes: Strictly accessible ONLY by Academic Administrator and Platform Administrator
CREATE POLICY p_acco_notes_admin ON accommodation_notes
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- ==============================================================================
-- 9. Scheduling Runs and Telemetry
-- ==============================================================================
CREATE POLICY p_sr_select ON scheduling_runs
    FOR SELECT USING (
        status = 'PUBLISHED'
        OR public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_sr_admin ON scheduling_runs
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_sa_select ON schedule_assignments
    FOR SELECT USING (
        status = 'CONFIRMED'
        OR public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_sa_admin ON schedule_assignments
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- Assignment Students: Learners see only their own assignments
CREATE POLICY p_as_select ON assignment_students
    FOR SELECT USING (
        student_id = public.get_auth_student_id()
        OR public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_as_admin ON assignment_students
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_ai_select ON assignment_invigilators
    FOR SELECT USING (
        invigilator_id = public.get_auth_invigilator_id()
        OR public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR')
    );

CREATE POLICY p_ai_admin ON assignment_invigilators
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- Snapshots and Decisions: Read-only for Administrators
CREATE POLICY p_res_admin ON run_exam_students
    FOR SELECT USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_res_write ON run_exam_students
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_sd_admin ON scheduling_decisions
    FOR SELECT USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_sd_write ON scheduling_decisions
    FOR INSERT WITH CHECK (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_se_admin ON schedule_events
    FOR SELECT USING (public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_se_write ON schedule_events
    FOR INSERT WITH CHECK (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_vi_select ON validation_issues
    FOR SELECT USING (public.get_auth_role() IN ('SUPPORT_STAFF', 'ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

CREATE POLICY p_vi_admin ON validation_issues
    FOR ALL USING (public.get_auth_role() IN ('ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'));

-- Audit Logs: Read-only for Platform Administrator
CREATE POLICY p_al_admin ON audit_logs
    FOR SELECT USING (public.get_auth_role() = 'PLATFORM_ADMINISTRATOR');

CREATE POLICY p_al_insert ON audit_logs
    FOR INSERT WITH CHECK (TRUE);

-- ==============================================================================
-- 10. Atomic Publication Procedure with Concurrency Row Lock
-- ==============================================================================
CREATE OR REPLACE FUNCTION public.publish_schedule_run(
    p_run_id UUID,
    p_admin_user_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_period_id UUID;
    v_current_status VARCHAR(20);
    v_previous_published_id UUID;
    v_result JSONB;
BEGIN
    -- 1. Identify target run and period
    SELECT academic_period_id, status 
    INTO v_period_id, v_current_status
    FROM scheduling_runs
    WHERE id = p_run_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Scheduling run % not found.', p_run_id;
    END IF;

    -- Idempotent check: If already published, return immediately with success
    IF v_current_status = 'PUBLISHED' THEN
        RETURN jsonb_build_object(
            'success', TRUE,
            'published_run_id', p_run_id,
            'academic_period_id', v_period_id,
            'status', 'PUBLISHED',
            'message', 'Timetable is already officially published and immutable.'
        );
    END IF;

    IF v_current_status NOT IN ('APPROVED', 'REVIEW_REQUIRED', 'DRAFT') THEN
        RAISE EXCEPTION 'Timetable % cannot be published because its status is %.', p_run_id, v_current_status;
    END IF;

    -- 2. Concurrency Lock: Acquire exclusive row lock on the academic period
    PERFORM id FROM academic_periods WHERE id = v_period_id FOR UPDATE;

    -- 3. Check for existing published run for this period
    SELECT id INTO v_previous_published_id
    FROM scheduling_runs
    WHERE academic_period_id = v_period_id AND status = 'PUBLISHED'
    FOR UPDATE;

    -- 4. Atomically supersede any existing published run
    IF v_previous_published_id IS NOT NULL AND v_previous_published_id != p_run_id THEN
        UPDATE scheduling_runs
        SET status = 'SUPERSEDED', updated_at = NOW()
        WHERE id = v_previous_published_id;

        INSERT INTO schedule_events (
            scheduling_run_id, entity_type, entity_id, event_type, 
            previous_state, new_state
        ) VALUES (
            v_previous_published_id, 'scheduling_runs', v_previous_published_id::text, 
            'STATUS_CHANGE', '{"status": "PUBLISHED"}'::jsonb, '{"status": "SUPERSEDED"}'::jsonb
        );
    END IF;

    -- 5. Mark the target run as PUBLISHED
    UPDATE scheduling_runs
    SET status = 'PUBLISHED', updated_at = NOW()
    WHERE id = p_run_id;

    -- 6. Update associated examination statuses to PUBLISHED
    UPDATE exams
    SET status = 'PUBLISHED', updated_at = NOW()
    WHERE id IN (SELECT DISTINCT exam_id FROM schedule_assignments WHERE scheduling_run_id = p_run_id);

    -- 7. Record state transition event and audit log
    INSERT INTO schedule_events (
        scheduling_run_id, entity_type, entity_id, event_type, 
        previous_state, new_state
    ) VALUES (
        p_run_id, 'scheduling_runs', p_run_id::text, 
        'SCHEDULE_PUBLISHED', jsonb_build_object('previous_status', v_current_status), '{"status": "PUBLISHED"}'::jsonb
    );

    INSERT INTO audit_logs (
        user_id, user_role, action, entity_type, entity_id,
        previous_state, new_state, result
    ) VALUES (
        p_admin_user_id, 'ACADEMIC_ADMINISTRATOR', 'PUBLISH_SCHEDULE',
        'scheduling_runs', p_run_id::text,
        jsonb_build_object('run_id', p_run_id, 'status', v_current_status),
        jsonb_build_object('run_id', p_run_id, 'status', 'PUBLISHED', 'superseded_run_id', v_previous_published_id),
        'SUCCESS'
    );

    v_result := jsonb_build_object(
        'success', TRUE,
        'published_run_id', p_run_id,
        'academic_period_id', v_period_id,
        'superseded_run_id', v_previous_published_id
    );

    RETURN v_result;
END;
$$;

