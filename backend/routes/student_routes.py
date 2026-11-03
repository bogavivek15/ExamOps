"""
ExamOps Student Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import List, Dict, Any, Optional
from backend.auth import get_current_user, CurrentUser, require_roles
from backend.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("")
def list_students(
    response: Response,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists students with optional keyword search across code, name, and email.
    Learners are strictly isolated to viewing only their own record."""
    if current_user.role in ("LEARNER", "STUDENT"):
        if current_user.student_id:
            stu = StudentService.get_student_by_id(current_user.student_id)
            items = [stu] if stu else []
            response.headers["X-Total-Count"] = str(len(items))
            return items
        response.headers["X-Total-Count"] = "0"
        return []

    items, total = StudentService.list_students(limit=limit, offset=offset, search=search)
    response.headers["X-Total-Count"] = str(total)
    return items

@router.get("/{student_id}")
def get_student(
    student_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves detailed profile for a specific student."""
    if current_user.role in ("LEARNER", "STUDENT") and current_user.student_id != student_id:
        raise HTTPException(status_code=403, detail="Forbidden: You may only view your own student record.")

    student = StudentService.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/{student_id}/enrollments")
def get_student_enrollments(
    student_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves all active course enrollments for a specific student."""
    if current_user.role in ("LEARNER", "STUDENT") and current_user.student_id != student_id:
        raise HTTPException(status_code=403, detail="Forbidden: You may only view your own enrollments.")

    return StudentService.get_student_enrollments(student_id)

@router.get("/{student_id}/schedule")
def get_student_schedule(
    student_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Retrieves the confirmed examination schedule for a student.
    Enforces that students can only inspect their own schedule unless the user is staff/admin.
    """
    if current_user.role in ("LEARNER", "STUDENT") and current_user.student_id != student_id:
        raise HTTPException(status_code=403, detail="Forbidden: You may only view your own schedule.")
    
    return StudentService.get_student_schedule(student_id)

