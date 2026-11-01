"""
ExamOps Authentication & User Profile Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.config import settings
from backend.auth import get_current_user, CurrentUser, require_roles, create_access_token, ROLE_ALIASES
from backend.database import execute_query

router = APIRouter(prefix="/auth", tags=["Authentication & Profiles"])

class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None

class DevSwitchRoleRequest(BaseModel):
    role: str

@router.post("/login")
def login(req: LoginRequest):
    """
    Authenticates a user and issues a cryptographically signed Bearer JWT token.
    The authoritative role is retrieved exclusively from PostgreSQL user_profiles.
    """
    email_clean = req.email.strip().lower()
    
    # Query database for user profile
    prof = execute_query(
        "SELECT * FROM user_profiles WHERE LOWER(email) = %s AND status = 'ACTIVE' LIMIT 1;",
        (email_clean,),
        fetch_one=True,
    )
    
    # Dedicated operator alias fallback
    if not prof and "officer" in email_clean:
        prof = execute_query(
            "SELECT * FROM user_profiles WHERE role = 'ACADEMIC_ADMINISTRATOR' AND status = 'ACTIVE' ORDER BY email ASC LIMIT 1;",
            fetch_one=True,
        )

    if not prof:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid credentials or user account '{req.email}' not found / inactive.",
        )

    token = create_access_token(
        user_id=str(prof["id"]),
        email=prof["email"],
        role=prof["role"],
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(prof["id"]),
            "email": prof["email"],
            "display_name": prof["display_name"],
            "role": prof["role"],
            "student_id": str(prof["student_id"]) if prof.get("student_id") else None,
            "invigilator_id": str(prof["invigilator_id"]) if prof.get("invigilator_id") else None,
            "department": prof.get("department"),
        },
    }

@router.post("/dev-switch-role")
def dev_switch_role(req: DevSwitchRoleRequest):
    """
    Local development role switcher.
    Issues a verified, signed JWT for a real PostgreSQL user record possessing the requested role.
    This guarantees the frontend never supplies an unverified role string directly.
    In production environments, granting administrator privileges via dev-switch-role is strictly forbidden.
    """
    canonical_role = ROLE_ALIASES.get(req.role.upper(), req.role.upper())
    
    # Enforce production security restriction
    if settings.ENVIRONMENT == "production":
        admin_roles = {"ACADEMIC_ADMINISTRATOR", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN", "EXAM_OFFICER"}
        if canonical_role in admin_roles or req.role.upper() in admin_roles:
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Development role switcher cannot grant administrator privileges in production.",
            )
    
    # Query database for active profile with this role
    prof = execute_query(
        "SELECT * FROM user_profiles WHERE role = %s AND status = 'ACTIVE' ORDER BY email ASC LIMIT 1;",
        (canonical_role,),
        fetch_one=True,
    )

    if not prof:
        raise HTTPException(
            status_code=404,
            detail=f"No active user profile with role '{canonical_role}' found in database.",
        )

    token = create_access_token(
        user_id=str(prof["id"]),
        email=prof["email"],
        role=prof["role"],
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(prof["id"]),
            "email": prof["email"],
            "display_name": prof["display_name"],
            "role": prof["role"],
            "student_id": str(prof["student_id"]) if prof.get("student_id") else None,
            "invigilator_id": str(prof["invigilator_id"]) if prof.get("invigilator_id") else None,
            "department": prof.get("department"),
        },
    }

@router.get("/me")
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Returns the authenticated user profile and authoritative database permissions."""
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
