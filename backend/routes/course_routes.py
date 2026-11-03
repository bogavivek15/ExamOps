"""
ExamOps Course & Enrollment Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.auth import get_current_user, CurrentUser
from backend.services.course_service import CourseService

router = APIRouter(tags=["Courses & Enrollments"])

@router.get("/courses")
def list_courses(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    department: Optional[str] = None,
    search: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists courses with optional department and search filters."""
    return CourseService.list_courses(limit=limit, offset=offset, department=department, search=search)

@router.get("/courses/{course_id}")
def get_course(
    course_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves course details."""
    course = CourseService.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/enrollments")
def list_enrollments(
    course_id: Optional[str] = None,
    student_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists student course enrollments.
    Learners are restricted strictly to viewing their own enrollments."""
    effective_student_id = student_id
    if current_user.role in ("LEARNER", "STUDENT"):
        if not current_user.student_id:
            return []
        effective_student_id = current_user.student_id

    return CourseService.list_enrollments(course_id=course_id, student_id=effective_student_id, limit=limit)

