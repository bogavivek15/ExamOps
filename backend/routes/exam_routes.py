"""
ExamOps Examination Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.auth import get_current_user, CurrentUser
from backend.services.course_service import ExamService

router = APIRouter(prefix="/exams", tags=["Examinations"])

@router.get("")
def list_exams(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists examinations with enrolled student counts."""
    return ExamService.list_exams(limit=limit, offset=offset, status=status, search=search)

@router.get("/{exam_id}")
def get_exam(
    exam_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves detailed examination record."""
    exam = ExamService.get_exam_by_id(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")
    return exam

@router.get("/{exam_id}/requirements")
def get_exam_requirements(
    exam_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves equipment and physical requirements for an examination."""
    return ExamService.get_exam_requirements(exam_id)

