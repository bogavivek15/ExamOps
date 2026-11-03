"""
ExamOps Invigilator Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.auth import get_current_user, CurrentUser
from backend.services.invigilator_service import InvigilatorService

router = APIRouter(prefix="/invigilators", tags=["Invigilators"])

@router.get("")
def list_invigilators(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    department: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists invigilators and staffing profiles."""
    if current_user.role in ("LEARNER", "STUDENT"):
        raise HTTPException(status_code=403, detail="Forbidden: Invigilator records are restricted to academic staff.")

    return InvigilatorService.list_invigilators(
        limit=limit,
        offset=offset,
        search=search,
        department=department,
    )

@router.get("/{invigilator_id}")
def get_invigilator(
    invigilator_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves detailed invigilator record."""
    if current_user.role in ("LEARNER", "STUDENT"):
        raise HTTPException(status_code=403, detail="Forbidden: Invigilator records are restricted to academic staff.")

    inv = InvigilatorService.get_invigilator_by_id(invigilator_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invigilator not found")
    return inv

@router.get("/{invigilator_id}/availabilities")
def get_invigilator_availabilities(
    invigilator_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves availability windows for an invigilator."""
    if current_user.role in ("LEARNER", "STUDENT", "INSTRUCTOR"):
        raise HTTPException(status_code=403, detail="Forbidden: Invigilator availability is restricted to operational staff.")

    return InvigilatorService.get_invigilator_availabilities(invigilator_id)

@router.get("/{invigilator_id}/schedule")
def get_invigilator_schedule(
    invigilator_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Retrieves confirmed examination assignments for an invigilator.
    Restricts invigilator self-inspection if user is of role INVIGILATOR or SUPPORT_STAFF with invigilator_id.
    """
    if current_user.role in ("LEARNER", "STUDENT", "INSTRUCTOR"):
        raise HTTPException(status_code=403, detail="Forbidden: Invigilator schedules are restricted to operational staff.")

    if current_user.role in ("SUPPORT_STAFF", "INVIGILATOR") and current_user.invigilator_id and current_user.invigilator_id != invigilator_id:
        raise HTTPException(status_code=403, detail="Forbidden: You may only view your own assignments.")
    return InvigilatorService.get_invigilator_assignments(invigilator_id)

