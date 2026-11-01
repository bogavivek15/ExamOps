-- ==============================================================================
-- ExamOps PostgreSQL Migration: 001_core_master_and_security.sql
-- Description: Core reference master data, security functions, user profiles,
--              courses, instructors, enrollments, exams, physical facilities,
--              invigilators, availabilities, and accommodations.
-- Entities Created: 17 of 26
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================================================
-- 1. Academic Periods
-- ==============================================================================
CREATE TABLE IF NOT EXISTS academic_periods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    exam_start_date DATE NOT NULL,
    exam_end_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_ap_dates CHECK (end_date >= start_date),
    CONSTRAINT chk_ap_exam_dates CHECK (
        exam_end_date >= exam_start_date 
        AND exam_start_date >= start_date 
        AND exam_end_date <= end_date
    )
);

CREATE INDEX IF NOT EXISTS idx_ap_code ON academic_periods(code);
CREATE INDEX IF NOT EXISTS idx_ap_is_active ON academic_periods(is_active);

-- ==============================================================================
-- 2. Students Master
-- ==============================================================================
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_code VARCHAR(32) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    program VARCHAR(150) NOT NULL,
    year_of_study INTEGER NOT NULL CHECK (year_of_study BETWEEN 1 AND 6),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
        CHECK (status IN ('ACTIVE', 'INACTIVE', 'GRADUATED', 'SUSPENDED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_student_code_format CHECK (student_code ~ '^STU-[0-9]{6}$')
);

CREATE INDEX IF NOT EXISTS idx_students_student_code ON students(student_code);
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);

-- ==============================================================================
-- 3. Invigilators Master
-- ==============================================================================
CREATE TABLE IF NOT EXISTS invigilators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invigilator_code VARCHAR(32) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    max_hours_per_day NUMERIC(4, 2) NOT NULL DEFAULT 8.00 
        CHECK (max_hours_per_day > 0 AND max_hours_per_day <= 24.00),
    max_hours_per_week NUMERIC(4, 2) NOT NULL DEFAULT 25.00 
        CHECK (max_hours_per_week > 0 AND max_hours_per_week <= 168.00),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
        CHECK (status IN ('ACTIVE', 'ON_LEAVE', 'INACTIVE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_invigilator_code_format CHECK (invigilator_code ~ '^INV-[0-9]{6}$')
);

CREATE INDEX IF NOT EXISTS idx_invigilators_code ON invigilators(invigilator_code);
CREATE INDEX IF NOT EXISTS idx_invigilators_email ON invigilators(email);
CREATE INDEX IF NOT EXISTS idx_invigilators_status ON invigilators(status);

-- ==============================================================================
-- 4. User Profiles & Authentication Linkage
-- ==============================================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(150) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'LEARNER' 
        CHECK (role IN ('LEARNER', 'INSTRUCTOR', 'ACADEMIC_ADMINISTRATOR', 'SUPPORT_STAFF', 'PLATFORM_ADMINISTRATOR')),
    student_id UUID UNIQUE REFERENCES students(id) ON DELETE RESTRICT,
    invigilator_id UUID UNIQUE REFERENCES invigilators(id) ON DELETE RESTRICT,
    department VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
        CHECK (status IN ('ACTIVE', 'SUSPENDED', 'INACTIVE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON user_profiles(role);
CREATE INDEX IF NOT EXISTS idx_user_profiles_student_id ON user_profiles(student_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_invigilator_id ON user_profiles(invigilator_id);

-- Helper functions for non-recursive RLS policy checks
CREATE OR REPLACE FUNCTION public.get_auth_role()
RETURNS TEXT
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT role FROM public.user_profiles WHERE id = auth.uid();
$$;

CREATE OR REPLACE FUNCTION public.get_auth_student_id()
RETURNS UUID
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT student_id FROM public.user_profiles WHERE id = auth.uid();
$$;

CREATE OR REPLACE FUNCTION public.get_auth_invigilator_id()
RETURNS UUID
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT invigilator_id FROM public.user_profiles WHERE id = auth.uid();
$$;

-- Trigger enforcing role and identity foreign-key immutability for non-platform-admins
CREATE OR REPLACE FUNCTION public.check_user_profile_immutability()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.role IS DISTINCT FROM OLD.role OR 
        NEW.student_id IS DISTINCT FROM OLD.student_id OR 
        NEW.invigilator_id IS DISTINCT FROM OLD.invigilator_id) THEN
        IF public.get_auth_role() != 'PLATFORM_ADMINISTRATOR' AND auth.uid() IS NOT NULL THEN
            RAISE EXCEPTION 'Unauthorized: only PLATFORM_ADMINISTRATOR can modify role or identity mappings.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS trg_user_profile_immutability ON user_profiles;
CREATE TRIGGER trg_user_profile_immutability
BEFORE UPDATE ON user_profiles
FOR EACH ROW EXECUTE FUNCTION public.check_user_profile_immutability();

-- ==============================================================================
-- 5. Courses Master
-- ==============================================================================
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    department VARCHAR(100) NOT NULL,
    credits INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 12),
    academic_period_id UUID NOT NULL REFERENCES academic_periods(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
        CHECK (status IN ('ACTIVE', 'ARCHIVED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_course_code_format CHECK (course_code ~ '^CRS-[0-9]{6}$'),
    CONSTRAINT uq_course_period UNIQUE (id, academic_period_id)
);

CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(course_code);
CREATE INDEX IF NOT EXISTS idx_courses_academic_period ON courses(academic_period_id);
CREATE INDEX IF NOT EXISTS idx_courses_department ON courses(department);

-- ==============================================================================
-- 6. Course Instructors
-- ==============================================================================
CREATE TABLE IF NOT EXISTS course_instructors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    instructor_profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE RESTRICT,
    role VARCHAR(30) NOT NULL DEFAULT 'PRIMARY_INSTRUCTOR' 
        CHECK (role IN ('PRIMARY_INSTRUCTOR', 'CO_INSTRUCTOR', 'TEACHING_ASSISTANT')),
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_course_instructor UNIQUE (course_id, instructor_profile_id)
);

CREATE INDEX IF NOT EXISTS idx_ci_course_id ON course_instructors(course_id);
CREATE INDEX IF NOT EXISTS idx_ci_instructor_profile_id ON course_instructors(instructor_profile_id);

-- ==============================================================================
-- 7. Enrollments
-- ==============================================================================
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_code VARCHAR(32) NOT NULL UNIQUE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE RESTRICT,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    academic_period_id UUID NOT NULL REFERENCES academic_periods(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
        CHECK (status IN ('ACTIVE', 'WITHDRAWN', 'COMPLETED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_enrollment_code_format CHECK (enrollment_code ~ '^ENR-[0-9]{6}$'),
    CONSTRAINT uq_enr_student_course UNIQUE (student_id, course_id, academic_period_id)
);

CREATE INDEX IF NOT EXISTS idx_enr_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enr_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enr_period_id ON enrollments(academic_period_id);

-- ==============================================================================
-- 8. Examinations
-- ==============================================================================
CREATE TABLE IF NOT EXISTS exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_code VARCHAR(32) NOT NULL UNIQUE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    academic_period_id UUID NOT NULL REFERENCES academic_periods(id) ON DELETE RESTRICT,
    title VARCHAR(200) NOT NULL,
    exam_type VARCHAR(20) NOT NULL DEFAULT 'FINAL' 
        CHECK (exam_type IN ('FINAL', 'MIDTERM', 'SUPPLEMENTARY')),
    duration_minutes INTEGER NOT NULL 
        CHECK (duration_minutes > 0 AND duration_minutes <= 480),
    priority INTEGER NOT NULL DEFAULT 3 
        CHECK (priority BETWEEN 1 AND 5),
    status VARCHAR(20) NOT NULL DEFAULT 'READY' 
        CHECK (status IN ('DRAFT', 'READY', 'SCHEDULED', 'CONFIRMED', 'PUBLISHED', 'CANCELLED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_exam_code_format CHECK (exam_code ~ '^EXAM-[0-9]{4}-[0-9]{6}$'),
    CONSTRAINT uq_exam_course_period UNIQUE (id, course_id, academic_period_id)
);

CREATE INDEX IF NOT EXISTS idx_exams_code ON exams(exam_code);
CREATE INDEX IF NOT EXISTS idx_exams_course ON exams(course_id);
CREATE INDEX IF NOT EXISTS idx_exams_period ON exams(academic_period_id);
CREATE INDEX IF NOT EXISTS idx_exams_status ON exams(status);

-- ==============================================================================
-- 9. Exam Requirements
-- ==============================================================================
CREATE TABLE IF NOT EXISTS exam_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_code VARCHAR(32) NOT NULL UNIQUE,
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    requirement_type VARCHAR(50) NOT NULL 
        CHECK (requirement_type IN ('REQUIRED_EQUIPMENT', 'ROOM_FEATURE', 'ROOM_CAPACITY_MIN')),
    value TEXT NOT NULL,
    unit VARCHAR(20),
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_req_code_format CHECK (requirement_code ~ '^REQ-[0-9]{6}$')
);

CREATE INDEX IF NOT EXISTS idx_req_exam_id ON exam_requirements(exam_id);
CREATE INDEX IF NOT EXISTS idx_req_type ON exam_requirements(requirement_type);

-- ==============================================================================
-- 10. Rooms Master
-- ==============================================================================
CREATE TABLE IF NOT EXISTS rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    building VARCHAR(100) NOT NULL,
    floor INTEGER NOT NULL,
    is_accessible BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE' 
        CHECK (status IN ('AVAILABLE', 'MAINTENANCE', 'CLOSED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_room_code_format CHECK (room_code ~ '^ROOM-[0-9]{6}$')
);

CREATE INDEX IF NOT EXISTS idx_rooms_code ON rooms(room_code);
CREATE INDEX IF NOT EXISTS idx_rooms_building ON rooms(building);
CREATE INDEX IF NOT EXISTS idx_rooms_accessible ON rooms(is_accessible);
CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status);

-- ==============================================================================
-- 11. Room Capacities
-- ==============================================================================
CREATE TABLE IF NOT EXISTS room_capacities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capacity_code VARCHAR(32) NOT NULL UNIQUE,
    room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    standard_capacity INTEGER NOT NULL CHECK (standard_capacity > 0),
    exam_capacity INTEGER NOT NULL CHECK (exam_capacity > 0 AND exam_capacity <= standard_capacity),
    effective_start DATE NOT NULL,
    effective_end DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_capacity_code_format CHECK (capacity_code ~ '^CAP-[0-9]{6}$'),
    CONSTRAINT chk_rc_dates CHECK (effective_end >= effective_start)
);

CREATE INDEX IF NOT EXISTS idx_rc_room_id ON room_capacities(room_id);
CREATE INDEX IF NOT EXISTS idx_rc_dates ON room_capacities(effective_start, effective_end);

-- ==============================================================================
-- 12. Equipment Types Catalog
-- ==============================================================================
CREATE TABLE IF NOT EXISTS equipment_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(30) NOT NULL 
        CHECK (category IN ('AV', 'COMPUTING', 'LABORATORY', 'ACCESSIBILITY')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_et_code ON equipment_types(code);
CREATE INDEX IF NOT EXISTS idx_et_category ON equipment_types(category);

-- ==============================================================================
-- 13. Room Equipment Inventory
-- ==============================================================================
CREATE TABLE IF NOT EXISTS room_equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    equipment_type_id UUID NOT NULL REFERENCES equipment_types(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity >= 1),
    status VARCHAR(20) NOT NULL DEFAULT 'OPERATIONAL' 
        CHECK (status IN ('OPERATIONAL', 'DEFECTIVE', 'REMOVED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_room_equipment UNIQUE (room_id, equipment_type_id)
);

CREATE INDEX IF NOT EXISTS idx_req_room_id ON room_equipment(room_id);
CREATE INDEX IF NOT EXISTS idx_req_equipment_type ON room_equipment(equipment_type_id);

-- ==============================================================================
-- 14. Room Availabilities & Closures
-- ==============================================================================
CREATE TABLE IF NOT EXISTS room_availabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    day_of_week INTEGER CHECK (day_of_week BETWEEN 0 AND 6),
    specific_date DATE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    availability_type VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE' 
        CHECK (availability_type IN ('AVAILABLE', 'CLOSED', 'MAINTENANCE')),
    effective_start DATE NOT NULL,
    effective_end DATE NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_ra_time CHECK (end_time > start_time),
    CONSTRAINT chk_ra_dates CHECK (effective_end >= effective_start),
    CONSTRAINT chk_ra_dow_or_date CHECK (
        (day_of_week IS NOT NULL) OR (specific_date IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_ra_room_id ON room_availabilities(room_id);
CREATE INDEX IF NOT EXISTS idx_ra_specific_date ON room_availabilities(specific_date);
CREATE INDEX IF NOT EXISTS idx_ra_dates ON room_availabilities(effective_start, effective_end);

-- ==============================================================================
-- 15. Invigilator Availabilities
-- ==============================================================================
CREATE TABLE IF NOT EXISTS availabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    availability_code VARCHAR(32) NOT NULL UNIQUE,
    invigilator_id UUID NOT NULL REFERENCES invigilators(id) ON DELETE RESTRICT,
    day_of_week INTEGER CHECK (day_of_week BETWEEN 0 AND 6),
    specific_date DATE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    availability_type VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE' 
        CHECK (availability_type IN ('AVAILABLE', 'UNAVAILABLE')),
    effective_start DATE NOT NULL,
    effective_end DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_avail_code_format CHECK (availability_code ~ '^AVL-[0-9]{6}$'),
    CONSTRAINT chk_avail_time CHECK (end_time > start_time),
    CONSTRAINT chk_avail_dates CHECK (effective_end >= effective_start),
    CONSTRAINT chk_avail_dow_or_date CHECK (
        (day_of_week IS NOT NULL) OR (specific_date IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_avail_invigilator_id ON availabilities(invigilator_id);
CREATE INDEX IF NOT EXISTS idx_avail_specific_date ON availabilities(specific_date);
CREATE INDEX IF NOT EXISTS idx_avail_dates ON availabilities(effective_start, effective_end);

-- ==============================================================================
-- 16. Student Accommodations
-- ==============================================================================
CREATE TABLE IF NOT EXISTS accommodations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accommodation_code VARCHAR(32) NOT NULL UNIQUE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE RESTRICT,
    accommodation_type VARCHAR(50) NOT NULL 
        CHECK (accommodation_type IN ('EXTENDED_TIME', 'ACCESSIBLE_ROOM', 'LOW_DISTRACTION', 'SPECIAL_EQUIPMENT')),
    extra_time_minutes INTEGER CHECK (extra_time_minutes IS NULL OR extra_time_minutes > 0),
    extra_time_percentage NUMERIC(5, 2) CHECK (extra_time_percentage IS NULL OR extra_time_percentage > 0),
    required_room_feature TEXT,
    required_equipment TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    effective_start DATE NOT NULL,
    effective_end DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_acco_code_format CHECK (accommodation_code ~ '^ACO-[0-9]{6}$'),
    CONSTRAINT chk_acco_dates CHECK (effective_end >= effective_start)
);

CREATE INDEX IF NOT EXISTS idx_acco_student_id ON accommodations(student_id);
CREATE INDEX IF NOT EXISTS idx_acco_type ON accommodations(accommodation_type);
CREATE INDEX IF NOT EXISTS idx_acco_is_active ON accommodations(is_active);

-- ==============================================================================
-- 17. Accommodation Clinical Notes (Confidential)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS accommodation_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accommodation_id UUID NOT NULL UNIQUE REFERENCES accommodations(id) ON DELETE CASCADE,
    clinical_notes TEXT NOT NULL,
    approved_by UUID REFERENCES user_profiles(id) ON DELETE RESTRICT,
    documentation_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_acco_notes_id ON accommodation_notes(accommodation_id);
