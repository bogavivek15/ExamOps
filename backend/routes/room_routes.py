"""
ExamOps Room Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.auth import get_current_user, CurrentUser
from backend.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms & Facilities"])

@router.get("")
def list_rooms(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    building: Optional[str] = None,
    floor: Optional[int] = None,
    is_accessible: Optional[bool] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists institutional rooms with effective examination capacities."""
    return RoomService.list_rooms(
        limit=limit,
        offset=offset,
        search=search,
        building=building,
        floor=floor,
        is_accessible=is_accessible,
    )

@router.get("/{room_id}")
def get_room(
    room_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves room record."""
    room = RoomService.get_room_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.get("/{room_id}/capacities")
def get_room_capacities(
    room_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves effective capacity history for a room."""
    return RoomService.get_room_capacities(room_id)

@router.get("/{room_id}/equipment")
def get_room_equipment(
    room_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves verified equipment installed in a room."""
    return RoomService.get_room_equipment(room_id)

@router.get("/{room_id}/availabilities")
def get_room_availabilities(
    room_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves operating hours and maintenance closures for a room."""
    return RoomService.get_room_availabilities(room_id)

