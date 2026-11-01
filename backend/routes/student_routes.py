"""
ExamOps Student Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.auth import get_current_user, CurrentUser, require_roles
from backend.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("")
def list_students(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists students with optional keyword search across code, name, and email."""
    return StudentService.list_students(limit=limit, offset=offset, search=search)

@router.get("/{student_id}")
def get_student(
    student_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves detailed profile for a specific student."""
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
    if current_user.role == "STUDENT" and current_user.student_id != student_id:
        raise HTTPException(status_code=403, detail="Forbidden: You may only view your own schedule.")
    
    return StudentService.get_student_schedule(student_id)
