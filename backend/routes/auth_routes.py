"""
ExamOps Authentication & User Profile Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Header, Request
from typing import List, Dict, Any, Optional
import httpx
import secrets
import time
import threading
from collections import defaultdict
from pydantic import BaseModel
from backend.config import settings
from backend.auth import (
    get_current_user, CurrentUser, require_roles,
    create_access_token, ROLE_ALIASES, invalidate_profile_cache,
)
from backend.database import execute_query, get_db_cursor

router = APIRouter(prefix="/auth", tags=["Authentication & Profiles"])

class DemoRateLimiter:
    """Thread-safe in-memory sliding-window rate limiter for evaluation demo login."""
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        with self._lock:
            timestamps = self._requests[client_ip]
            valid = [t for t in timestamps if now - t < self.window_seconds]
            if len(valid) >= self.max_requests:
                self._requests[client_ip] = valid
                return False
            valid.append(now)
            self._requests[client_ip] = valid
            return True

    def reset(self):
        with self._lock:
            self._requests.clear()

_demo_rate_limiter = DemoRateLimiter(max_requests=30, window_seconds=60)

class UpdateProfileRequest(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None
    display_name: Optional[str] = None
    department: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None

class DevSwitchRoleRequest(BaseModel):
    role: str

class DemoLoginRequest(BaseModel):
    role: str

ALLOWED_DEMO_ROLES = {
    "ACADEMIC_ADMINISTRATOR",
    "INSTRUCTOR",
    "SUPPORT_STAFF",
    "LEARNER",
}

DEMO_ROLE_ACCOUNTS: Dict[str, Dict[str, str]] = {
    "ACADEMIC_ADMINISTRATOR": {
        "email": "evaluator@examops.edu",
        "title": "Academic Administrator",
        "description": "Full operational authority over timetables, constraints, room allocations, exception triage, and publication.",
    },
    "INSTRUCTOR": {
        "email": "head.computer@faculty.institution.edu",
        "title": "Instructor",
        "description": "Departmental curriculum view, student cohort enrollments, and schedule examination details.",
    },
    "SUPPORT_STAFF": {
        "email": "facilities.lead.1@examops.institution.edu",
        "title": "Support Staff",
        "description": "Invigilator duties, venue accessibility features, and proctoring schedules.",
    },
    "LEARNER": {
        "email": "carlos.garcia.0008@student.institution.edu",
        "title": "Learner",
        "description": "Student portal viewing personal exam timetables and venue locations without administrative controls.",
    },
}

@router.get("/demo-roles")
def list_demo_roles():
    """Returns the supported demo roles and their institutional descriptions for evaluation access."""
    if not settings.DEMO_LOGIN_ENABLED:
        raise HTTPException(
            status_code=403,
            detail="Demo evaluation access is currently disabled.",
        )
    return [
        {
            "id": role_id,
            "title": info["title"],
            "description": info["description"],
            "email": info["email"],
        }
        for role_id, info in DEMO_ROLE_ACCOUNTS.items()
        if role_id in ALLOWED_DEMO_ROLES
    ]

@router.post("/demo-login")
def demo_login(
    req: DemoLoginRequest,
    request: Request,
    x_demo_access_key: Optional[str] = Header(None, alias="X-Demo-Access-Key"),
):
    """
    Dedicated demo evaluation access endpoint.
    Issues a cryptographically signed Bearer session for the requested role.
    Strictly protected:
    1. Requires DEMO_LOGIN_ENABLED to be true.
    2. Enforces sliding-window rate limiting.
    3. Strictly forbids PLATFORM_ADMINISTRATOR and SUPER_ADMIN.
    4. Only permits the four authorized demo roles.
    5. Resolves role from active database profile and validates role match without fallback.
    """
    # 1. Reject if demo login is not explicitly enabled
    if not settings.DEMO_LOGIN_ENABLED:
        raise HTTPException(
            status_code=403,
            detail="Demo evaluation access is currently disabled.",
        )

    # 2. Rate limiting check
    client_ip = request.client.host if request.client else "127.0.0.1"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()

    if not _demo_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait a moment before requesting another demo session.",
        )

    # 3. Role validation
    requested_raw = (req.role or "").strip().upper()
    canonical_role = ROLE_ALIASES.get(requested_raw, requested_raw)

    # Never allow public demo login to issue a Platform Administrator or Super Admin token
    if canonical_role in ("PLATFORM_ADMINISTRATOR", "SUPER_ADMIN") or requested_raw in ("PLATFORM_ADMINISTRATOR", "SUPER_ADMIN"):
        raise HTTPException(
            status_code=403,
            detail="Platform Administrator access is strictly prohibited via demo login.",
        )

    # Only allow the four intended public demo roles
    if canonical_role not in ALLOWED_DEMO_ROLES or canonical_role not in DEMO_ROLE_ACCOUNTS:
        raise HTTPException(
            status_code=403,
            detail=f"Unsupported demo role '{req.role}'. Allowed demo roles: {sorted(list(ALLOWED_DEMO_ROLES))}",
        )

    # 4. Resolve role from active database profile for the designated account
    demo_info = DEMO_ROLE_ACCOUNTS[canonical_role]
    target_email = demo_info["email"]

    prof = execute_query(
        "SELECT * FROM user_profiles WHERE LOWER(email) = %s AND status = 'ACTIVE' LIMIT 1;",
        (target_email.lower(),),
        fetch_one=True,
    )

    if not prof:
        raise HTTPException(
            status_code=404,
            detail=f"No active demo account found for role '{canonical_role}'.",
        )

    # 5. Strict role verification: Verify the database profile's actual role matches the requested role
    # Never fall back to a different account or role!
    actual_db_role = prof.get("role")
    if actual_db_role != canonical_role:
        raise HTTPException(
            status_code=403,
            detail=f"Database profile role '{actual_db_role}' does not match requested role '{canonical_role}'.",
        )

    # Secondary safety assertion: Never issue a platform admin token under any circumstances
    if actual_db_role in ("PLATFORM_ADMINISTRATOR", "SUPER_ADMIN"):
        raise HTTPException(
            status_code=403,
            detail="Issuing Platform Administrator tokens via demo login is strictly prohibited.",
        )

    token = create_access_token(
        user_id=str(prof["id"]),
        email=prof["email"],
        role=actual_db_role,
    )

    invalidate_profile_cache()

    return {
        "access_token": token,
        "token_type": "bearer",
        "demo_mode": True,
        "user": {
            "id": str(prof["id"]),
            "email": prof["email"],
            "display_name": prof["display_name"],
            "role": actual_db_role,
            "student_id": str(prof["student_id"]) if prof.get("student_id") else None,
            "invigilator_id": str(prof["invigilator_id"]) if prof.get("invigilator_id") else None,
            "department": prof.get("department"),
        },
    }

@router.post("/login")
def login(req: LoginRequest):
    """
    Authenticates a user via Supabase Auth password verification and returns the authoritative user profile.
    Client-supplied passwords MUST be verified. Unauthenticated email-only logins are strictly forbidden.
    """
    email_clean = req.email.strip().lower() if req.email else ""
    if not email_clean or not req.password:
        raise HTTPException(
            status_code=400,
            detail="Both email and password are required.",
        )

    access_token = None
    auth_user_id = None

    # Step 1: Attempt Supabase Auth password verification via official API
    if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY and not settings.SUPABASE_ANON_KEY.startswith("placeholder"):
        try:
            r = httpx.post(
                f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/token?grant_type=password",
                headers={
                    "apikey": settings.SUPABASE_ANON_KEY,
                    "Content-Type": "application/json",
                },
                json={"email": email_clean, "password": req.password},
                timeout=5.0,
            )
            if r.status_code == 200:
                token_data = r.json()
                access_token = token_data.get("access_token")
                user_obj = token_data.get("user", {})
                auth_user_id = user_obj.get("id")
        except Exception:
            pass

    # Step 2: Fallback check against auth.users bcrypt password via direct PostgreSQL
    if not access_token:
        try:
            user_row = execute_query(
                """SELECT id, email, encrypted_password, email_confirmed_at
                   FROM auth.users
                   WHERE LOWER(email) = %s AND (encrypted_password = crypt(%s, encrypted_password));""",
                (email_clean, req.password),
                fetch_one=True,
            )
            if user_row:
                auth_user_id = str(user_row["id"])
                prof = execute_query(
                    "SELECT * FROM user_profiles WHERE (id = %s OR LOWER(email) = %s) AND status = 'ACTIVE' LIMIT 1;",
                    (auth_user_id, email_clean),
                    fetch_one=True,
                )
                if prof:
                    access_token = create_access_token(
                        user_id=str(prof["id"]),
                        email=prof["email"],
                        role=prof["role"],
                    )
        except Exception:
            pass

    if not access_token or not auth_user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    # Authoritative profile resolution from PostgreSQL user_profiles
    prof = execute_query(
        "SELECT * FROM user_profiles WHERE (id = %s OR LOWER(email) = %s) AND status = 'ACTIVE' LIMIT 1;",
        (auth_user_id, email_clean),
        fetch_one=True,
    )

    if not prof:
        raise HTTPException(
            status_code=401,
            detail=f"User authenticated but no active operational profile found for '{email_clean}'.",
        )

    invalidate_profile_cache()

    return {
        "access_token": access_token,
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
    Strictly disabled in production environments.
    """
    env = (settings.ENVIRONMENT or "").strip().lower()
    if env in ("production", "prod"):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Role switching is disabled in production environments.",
        )

    canonical_role = ROLE_ALIASES.get(req.role.upper(), req.role.upper())

    if canonical_role in ("PLATFORM_ADMINISTRATOR", "SUPER_ADMIN"):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Cannot switch to Platform Administrator role via dev switcher.",
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

    invalidate_profile_cache()

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

@router.patch("/profiles/{user_id}", dependencies=[Depends(require_roles("PLATFORM_ADMINISTRATOR", "SUPER_ADMIN"))])
def update_user_profile(
    user_id: str,
    req: UpdateProfileRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Updates a user profile (role, status, display name, department).
    Enforces atomic database update and immediate local cache invalidation.
    Cross-worker cache TTL ensures all workers converge within 5.0 seconds.
    """
    fields = []
    values = []

    if req.role is not None:
        canonical_role = ROLE_ALIASES.get(req.role.upper(), req.role.upper())
        fields.append("role = %s")
        values.append(canonical_role)
    if req.status is not None:
        fields.append("status = %s")
        values.append(req.status.upper())
    if req.display_name is not None:
        fields.append("display_name = %s")
        values.append(req.display_name)
    if req.department is not None:
        fields.append("department = %s")
        values.append(req.department)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    values.append(user_id)
    sql = f"""
    UPDATE user_profiles
    SET {', '.join(fields)}, updated_at = NOW()
    WHERE id = %s
    RETURNING id, email, display_name, role, status, department;
    """
    with get_db_cursor(commit=True) as cur:
        cur.execute(sql, tuple(values))
        updated = cur.fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail=f"User profile '{user_id}' not found.")

        invalidate_profile_cache(f"user:{user_id}")
        invalidate_profile_cache()
        return dict(updated)
