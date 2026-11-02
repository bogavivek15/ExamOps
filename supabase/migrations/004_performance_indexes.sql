-- ==============================================================================
-- ExamOps PostgreSQL Migration: 004_performance_indexes.sql
-- Description: Composite and high-performance covering indexes for sub-second queries.
-- ==============================================================================

-- 1. Index on assignment_students(scheduling_run_id) for rapid batch deletions and counts
CREATE INDEX IF NOT EXISTS idx_as_scheduling_run_id 
ON assignment_students(scheduling_run_id);

-- 2. Index on assignment_students(student_id, scheduling_run_id) for student schedule lookups
CREATE INDEX IF NOT EXISTS idx_as_student_run 
ON assignment_students(student_id, scheduling_run_id);

-- 3. Covering index on students(first_name, last_name, student_code) for rapid sorting & filtering
CREATE INDEX IF NOT EXISTS idx_students_names_code 
ON students(first_name, last_name, student_code);

-- 4. Composite index on enrollments(status, academic_period_id) for scheduling participant snapshots
CREATE INDEX IF NOT EXISTS idx_enr_status_period 
ON enrollments(academic_period_id, status);

-- 5. Composite index on courses(academic_period_id, department)
CREATE INDEX IF NOT EXISTS idx_courses_period_dept 
ON courses(academic_period_id, department);

-- 6. Composite index on exams(academic_period_id, status)
CREATE INDEX IF NOT EXISTS idx_exams_period_status 
ON exams(academic_period_id, status);

-- 7. Composite index on accommodations(is_active, effective_start, effective_end)
CREATE INDEX IF NOT EXISTS idx_acc_active_dates 
ON accommodations(is_active, effective_start, effective_end);

-- 8. Composite index on audit_logs(created_at DESC, action)
CREATE INDEX IF NOT EXISTS idx_al_created_action 
ON audit_logs(created_at DESC, action);

