"""
ExamOps Backend — Pydantic Schemas and Contracts
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional, Any
from datetime import date, time, datetime

# ------------------------------------------------------------------------------
# User & Profile Schemas
# ------------------------------------------------------------------------------
class UserProfileResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    student_id: Optional[str] = None
    invigilator_id: Optional[str] = None
    department: Optional[str] = None
    status: str

# ------------------------------------------------------------------------------
# Student Schemas
# ------------------------------------------------------------------------------
class StudentCreate(BaseModel):
    student_code: str
    first_name: str
    last_name: str
    email: str
    date_of_birth: date
    program: str
    year_of_study: int
    status: str = "ACTIVE"

class StudentResponse(StudentCreate):
    id: str
    created_at: Optional[datetime] = None

# ------------------------------------------------------------------------------
# Course & Enrollment Schemas
# ------------------------------------------------------------------------------
class CourseCreate(BaseModel):
    course_code: str
    name: str
    department: str
    credits: int
    academic_period_id: str
    status: str = "ACTIVE"

class CourseResponse(CourseCreate):
    id: str

class EnrollmentCreate(BaseModel):
    enrollment_code: str
    student_id: str
    course_id: str
    academic_period_id: str
    status: str = "ACTIVE"

class EnrollmentResponse(EnrollmentCreate):
    id: str

# ------------------------------------------------------------------------------
# Exam & Requirement Schemas
# ------------------------------------------------------------------------------
class ExamRequirementCreate(BaseModel):
    requirement_code: str
    requirement_type: str
    value: str
    unit: Optional[str] = None
    is_mandatory: bool = True

class ExamRequirementResponse(ExamRequirementCreate):
    id: str
    exam_id: str

class ExamCreate(BaseModel):
    exam_code: str
    course_id: str
    academic_period_id: str
    title: str
    exam_type: str = "FINAL"
    duration_minutes: int
    priority: int = 3
    status: str = "READY"

class ExamResponse(ExamCreate):
    id: str
    course_name: Optional[str] = None
    enrolled_student_count: Optional[int] = 0

# ------------------------------------------------------------------------------
# Room & Resource Schemas
# ------------------------------------------------------------------------------
class RoomCreate(BaseModel):
    room_code: str
    name: str
    building: str
    floor: int
    is_accessible: bool = False
    status: str = "AVAILABLE"

class RoomResponse(RoomCreate):
    id: str
    standard_capacity: Optional[int] = None
    exam_capacity: Optional[int] = None

# ------------------------------------------------------------------------------
# Invigilator Schemas
# ------------------------------------------------------------------------------
class InvigilatorCreate(BaseModel):
    invigilator_code: str
    first_name: str
    last_name: str
    email: str
    department: str
    max_hours_per_day: float = 8.0
    max_hours_per_week: float = 25.0
    status: str = "ACTIVE"

class InvigilatorResponse(InvigilatorCreate):
    id: str

# ------------------------------------------------------------------------------
# Accommodation Schemas
# ------------------------------------------------------------------------------
class AccommodationCreate(BaseModel):
    accommodation_code: str
    student_id: str
    accommodation_type: str
    extra_time_minutes: Optional[int] = None
    extra_time_percentage: Optional[float] = None
    required_room_feature: Optional[str] = None
    required_equipment: Optional[str] = None
    is_active: bool = True
    effective_start: date
    effective_end: date

class AccommodationResponse(AccommodationCreate):
    id: str
    student_name: Optional[str] = None

class AccommodationNoteCreate(BaseModel):
    accommodation_id: str
    clinical_notes: str
    documentation_url: Optional[str] = None

class AccommodationNoteResponse(AccommodationNoteCreate):
    id: str
    approved_by: Optional[str] = None

# ------------------------------------------------------------------------------
# Scheduling Schemas
# ------------------------------------------------------------------------------
class SchedulingRunCreate(BaseModel):
    academic_period_id: str
    algorithm_version: str = "1.0.0"
    seed: int = 20261022

class SchedulingRunResponse(BaseModel):
    id: str
    run_code: str
    academic_period_id: str
    created_by: Optional[str] = None
    algorithm_version: str
    seed: int
    status: str
    total_exams: int
    scheduled_count: int
    unassigned_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

class ScheduleAssignmentResponse(BaseModel):
    id: str
    assignment_code: str
    scheduling_run_id: str
    exam_id: str
    exam_code: Optional[str] = None
    exam_title: Optional[str] = None
    room_id: str
    room_code: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str
    seated_student_count: Optional[int] = 0

class DecisionResponse(BaseModel):
    id: str
    scheduling_run_id: str
    exam_id: str
    decision_order: int
    is_assigned: bool
    reason_codes: List[str]
    selected_candidate: Optional[Dict[str, Any]] = None
    candidate_details: Optional[Dict[str, Any]] = None

class ValidationIssueResponse(BaseModel):
    id: str
    scheduling_run_id: str
    exam_id: Optional[str] = None
    assignment_id: Optional[str] = None
    issue_type: str
    severity: str
    description: str
    resolution_status: str

# ------------------------------------------------------------------------------
# Analytics & Audit Schemas
# ------------------------------------------------------------------------------
class AnalyticsOverviewResponse(BaseModel):
    total_students: int
    total_courses: int
    total_exams: int
    total_rooms: int
    total_invigilators: int
    active_period_code: Optional[str] = None
    scheduled_exams: int
    unassigned_exams: int
    completion_rate_pct: float
    total_seated_registrations: int

class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    result: str
    created_at: datetime
