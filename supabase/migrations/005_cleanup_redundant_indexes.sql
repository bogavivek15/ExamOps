-- ==============================================================================
-- ExamOps PostgreSQL Migration: 005_cleanup_redundant_indexes.sql
-- Description: Drop redundant single-column indexes that duplicate primary/unique constraints.
-- Identified during post-optimization independent performance engineering audit.
-- ==============================================================================

-- 1. Drop redundant index on assignment_students(reservation_id)
-- Already enforced by unique constraint: assignment_students_reservation_id_key
DROP INDEX IF EXISTS idx_as_res_id;

-- 2. Drop redundant index on courses(course_code)
-- Already enforced by unique constraint: courses_course_code_key
DROP INDEX IF EXISTS idx_courses_code;

-- 3. Drop redundant index on exams(exam_code)
-- Already enforced by unique constraint: exams_exam_code_key
DROP INDEX IF EXISTS idx_exams_code;

-- 4. Drop redundant index on students(institutional_email)
-- Already enforced by unique constraint: students_institutional_email_key
DROP INDEX IF EXISTS idx_students_email;

-- 5. Drop redundant index on students(student_code)
-- Already enforced by unique constraint: students_student_code_key
DROP INDEX IF EXISTS idx_students_student_code;

