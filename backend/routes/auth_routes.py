"""
ExamOps Authentication & User Profile Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from backend.auth import get_current_user, CurrentUser, require_roles
from backend.database import execute_query

router = APIRouter(prefix="/auth", tags=["Authentication & Profiles"])

@router.get("/me")
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Returns the authenticated user profile and permissions."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "role": current_user.role,
        "student_id": current_user.student_id,
        "invigilator_id": current_user.invigilator_id,
        "department": current_user.department,
    }

@router.get("/profiles", dependencies=[Depends(require_roles("ACADEMIC_ADMINISTRATOR", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN"))])
def list_user_profiles(limit: int = 50, offset: int = 0):
    """Lists registered user profiles (restricted to administrators)."""
    return execute_query(
        "SELECT id, email, display_name, role, status, student_id, invigilator_id, department, created_at FROM user_profiles ORDER BY email ASC LIMIT %s OFFSET %s;",
        (limit, offset),
    )

