"""
ExamOps Accommodation Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.auth import get_current_user, CurrentUser, require_roles
from backend.services.accommodation_service import AccommodationService

router = APIRouter(prefix="/accommodations", tags=["Accommodations"])

@router.get("")
def list_accommodations(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    student_id: Optional[str] = None,
    accommodation_type: Optional[str] = None,
    active_only: bool = False,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists student accommodations (extra time, accessible rooms, low-distraction environments).
    Learners are restricted strictly to viewing their own accommodations."""
    effective_student_id = student_id
    if current_user.role in ("LEARNER", "STUDENT"):
        if not current_user.student_id:
            return []
        effective_student_id = current_user.student_id

    return AccommodationService.list_accommodations(
        limit=limit,
        offset=offset,
        student_id=effective_student_id,
        accommodation_type=accommodation_type,
        active_only=active_only,
    )

@router.get("/{acc_id}")
def get_accommodation(
    acc_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves specific accommodation record."""
    acc = AccommodationService.get_accommodation_by_id(acc_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Accommodation not found")
    if current_user.role in ("LEARNER", "STUDENT") and str(acc.get("student_id")) != str(current_user.student_id):
        raise HTTPException(status_code=403, detail="Forbidden: You may only view your own accommodations.")
    return acc

@router.get("/{acc_id}/notes")
def get_accommodation_notes(
    acc_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Retrieves clinical notes associated with an accommodation.
    Redacts medical information unless the caller is SUPER_ADMIN or EXAM_OFFICER.
    """
    return AccommodationService.get_accommodation_notes(acc_id, viewer_role=current_user.role)

