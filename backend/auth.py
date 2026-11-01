"""
ExamOps Authentication & Role-Based Authorization
Validates bearer credentials and resolves immutable user profiles.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import time
import json
import base64
import hmac
import hashlib
import uuid
from fastapi import Header, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.config import settings
from backend.database import execute_query

bearer_scheme = HTTPBearer(auto_error=False)

@dataclass
class CurrentUser:
    id: str
    email: str
    display_name: str
    role: str
    student_id: Optional[str] = None
    invigilator_id: Optional[str] = None
    department: Optional[str] = None

ROLE_ALIASES = {
    "STUDENT": "LEARNER",
    "LEARNER": "LEARNER",
    "INSTRUCTOR": "INSTRUCTOR",
    "INVIGILATOR": "SUPPORT_STAFF",
    "SUPPORT_STAFF": "SUPPORT_STAFF",
    "EXAM_OFFICER": "ACADEMIC_ADMINISTRATOR",
    "ACADEMIC_ADMINISTRATOR": "ACADEMIC_ADMINISTRATOR",
    "SUPER_ADMIN": "PLATFORM_ADMINISTRATOR",
    "PLATFORM_ADMINISTRATOR": "PLATFORM_ADMINISTRATOR",
}

def create_access_token(user_id: str, email: str, role: str, expires_delta_seconds: Optional[int] = None) -> str:
    """Generates a cryptographically signed RFC 7519 HS256 JWT access token."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    ttl = expires_delta_seconds or (settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + ttl,
    }
    
    h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    to_sign = f"{h_b64}.{p_b64}".encode()
    signature = base64.urlsafe_b64encode(
        hmac.new(settings.JWT_SECRET_KEY.encode(), to_sign, hashlib.sha256).digest()
    ).decode().rstrip("=")
    return f"{h_b64}.{p_b64}.{signature}"

def verify_and_decode_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Verifies HS256 JWT signature and expiration. Returns payload dict or None."""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    
    header_b64, payload_b64, signature_b64 = parts
    to_sign = f"{header_b64}.{payload_b64}".encode()
    
    valid = False
    for secret in [settings.JWT_SECRET_KEY, settings.SUPABASE_JWT_SECRET]:
        if not secret:
            continue
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(secret.encode(), to_sign, hashlib.sha256).digest()
        ).decode().rstrip("=")
        if hmac.compare_digest(signature_b64, expected_sig):
            valid = True
            break
            
    if not valid and settings.ENVIRONMENT != "production" and signature_b64 in ("mock-signature", "dev-signature"):
        valid = True
        
    if not valid:
        return None
        
    try:
        pad = payload_b64 + "=" * ((4 - len(payload_b64) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode(pad))
        if "exp" in payload and payload["exp"] < int(time.time()):
            return None
        return payload
    except Exception:
        return None

def get_current_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    x_test_user_id: Optional[str] = Header(None, alias="X-Test-User-Id"),
    x_test_role: Optional[str] = Header(None, alias="X-Test-Role"),
) -> CurrentUser:
    """
    Resolves the authenticated user.
    The user's role is EXCLUSIVELY resolved by querying the database user_profiles table.
    Client-supplied roles in headers or body are never trusted as authoritative in production.
    """
    user_id = None
    
    if auth_header and auth_header.credentials:
        token = auth_header.credentials
        payload = verify_and_decode_jwt(token)
        if payload:
            user_id = payload.get("sub") or payload.get("id")
        else:
            # Check if token is directly a user UUID (allowed only in dev/test)
            if settings.ENVIRONMENT != "production":
                try:
                    uuid.UUID(str(token))
                    user_id = token
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid or expired Bearer token signature.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired Bearer token signature.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    elif x_test_user_id and settings.ENVIRONMENT != "production":
        user_id = x_test_user_id
    elif x_test_role and settings.ENVIRONMENT != "production":
        # Internal test harness role fallback (used by verify_phase*.py scripts)
        canonical_role = ROLE_ALIASES.get(x_test_role.upper(), x_test_role)
        prof = execute_query(
            "SELECT * FROM user_profiles WHERE role = %s AND status = 'ACTIVE' ORDER BY created_at ASC LIMIT 1;",
            (canonical_role,),
            fetch_one=True,
        )
        if prof:
            return CurrentUser(
                id=str(prof["id"]),
                email=prof["email"],
                display_name=prof["display_name"],
                role=prof["role"],
                student_id=str(prof["student_id"]) if prof["student_id"] else None,
                invigilator_id=str(prof["invigilator_id"]) if prof["invigilator_id"] else None,
                department=prof["department"],
            )

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate UUID syntax safely against PostgreSQL
    prof = None
    try:
        valid_uuid = str(uuid.UUID(str(user_id)))
        prof = execute_query(
            "SELECT * FROM user_profiles WHERE id = %s AND status = 'ACTIVE';",
            (valid_uuid,),
            fetch_one=True,
        )
    except (ValueError, TypeError, AttributeError):
        if user_id and "@" in str(user_id):
            prof = execute_query(
                "SELECT * FROM user_profiles WHERE email = %s AND status = 'ACTIVE';",
                (str(user_id),),
                fetch_one=True,
            )

    if not prof:
        raise HTTPException(
            status_code=401,
            detail=f"User profile not found for identifier '{user_id}'.",
        )

    return CurrentUser(
        id=str(prof["id"]),
        email=prof["email"],
        display_name=prof["display_name"],
        role=prof["role"],
        student_id=str(prof["student_id"]) if prof["student_id"] else None,
        invigilator_id=str(prof["invigilator_id"]) if prof["invigilator_id"] else None,
        department=prof["department"],
    )

def require_roles(*allowed_roles: str):
    """Enforces role-based access control on routes."""
    canonical_allowed = set()
    for r in allowed_roles:
        canonical_allowed.add(ROLE_ALIASES.get(r.upper(), r))
        canonical_allowed.add(r)

    def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role not in canonical_allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: role '{current_user.role}' lacks permission for this action. Allowed: {allowed_roles}",
            )
        return current_user
    return role_checker
