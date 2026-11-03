"""
ExamOps Authentication & Role-Based Authorization
Validates Supabase Bearer credentials (JWKS asymmetric ES256/RS256 and secret HS256)
and resolves immutable, authoritative user profiles from PostgreSQL.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
import threading
import time
import json
import base64
import hmac
import hashlib
import uuid
import httpx
from jose import jwt, jwk
from jose.exceptions import JWTError, ExpiredSignatureError
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

class ProfileCache:
    """Thread-safe bounded in-memory cache for user profiles to eliminate redundant DB lookups.
    Enforces a strict 5-second maximum TTL to guarantee immediate security revocation propagation."""
    def __init__(self, ttl_seconds: float = 5.0):
        self._cache: Dict[str, Tuple[float, CurrentUser]] = {}
        self._lock = threading.Lock()
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[CurrentUser]:
        now = time.time()
        with self._lock:
            entry = self._cache.get(key)
            if entry and (now - entry[0] < self.ttl):
                return entry[1]
            if entry:
                del self._cache[key]
            return None

    def set(self, key: str, user: CurrentUser):
        with self._lock:
            if len(self._cache) > 500:
                self._cache.clear()
            self._cache[key] = (time.time(), user)

    def invalidate(self, key: Optional[str] = None):
        with self._lock:
            if key:
                self._cache.pop(key, None)
            else:
                self._cache.clear()

    def clear(self):
        """Clears all entries from the profile cache."""
        self.invalidate()

_profile_cache = ProfileCache(ttl_seconds=5.0)

def invalidate_profile_cache(key: Optional[str] = None):
    """Invalidates the in-memory user profile cache."""
    _profile_cache.invalidate(key)

class JWKSCache:
    """Thread-safe cache for Supabase Auth JWKS public signing keys."""
    def __init__(self, supabase_url: str, ttl_seconds: float = 3600.0):
        self.supabase_url = supabase_url.rstrip("/") if supabase_url else ""
        self.ttl = ttl_seconds
        self._keys: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._last_fetch: float = 0.0

    def _fetch_keys(self):
        if not self.supabase_url or "placeholder" in self.supabase_url:
            return
        url = f"{self.supabase_url}/auth/v1/.well-known/jwks.json"
        try:
            r = httpx.get(url, timeout=5.0)
            if r.status_code == 200:
                data = r.json()
                new_keys = {}
                for k in data.get("keys", []):
                    kid = k.get("kid")
                    if kid:
                        new_keys[kid] = jwk.construct(k)
                self._keys = new_keys
                self._last_fetch = time.time()
        except Exception:
            pass

    def get_key(self, kid: Optional[str]) -> Optional[Any]:
        with self._lock:
            now = time.time()
            if not self._keys or (now - self._last_fetch > self.ttl) or (kid and kid not in self._keys):
                self._fetch_keys()
            if kid and kid in self._keys:
                return self._keys[kid]
            if len(self._keys) == 1 and not kid:
                return next(iter(self._keys.values()))
            return None

_jwks_cache = JWKSCache(settings.SUPABASE_URL)

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
    """
    Verifies JWT cryptographic signature, expiration, and issuer against:
    1. Supabase JWKS (ES256 / RS256 asymmetric keys) - requires exact Supabase issuer
    2. SUPABASE_JWT_SECRET (HS256) - requires exact Supabase issuer
    3. JWT_SECRET_KEY (HS256) - internal ExamOps tokens; preserves compatibility with tokens lacking an issuer
    Returns decoded payload dictionary or None if invalid.
    """
    if not token or not isinstance(token, str):
        return None

    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        return None

    alg = unverified_header.get("alg", "HS256")
    kid = unverified_header.get("kid")

    supabase_url = (settings.SUPABASE_URL or "").strip().rstrip("/")
    expected_iss = f"{supabase_url}/auth/v1" if supabase_url else ""

    # Step 1: Attempt JWKS / asymmetric decode (ES256 / RS256)
    if alg in ("ES256", "RS256"):
        key = _jwks_cache.get_key(kid)
        if not key:
            return None
        try:
            payload = jwt.decode(
                token,
                key,
                algorithms=[alg],
                options={"verify_signature": True, "verify_exp": True, "verify_aud": False},
            )
            # Requirement 1: require iss to exactly match SUPABASE_URL.rstrip("/") + "/auth/v1"
            if not expected_iss or payload.get("iss") != expected_iss:
                return None
            return payload
        except (JWTError, ExpiredSignatureError):
            return None
        except Exception:
            return None

    # Step 2: Attempt HS256 decode using SUPABASE_JWT_SECRET (if configured)
    supabase_secret = settings.SUPABASE_JWT_SECRET
    jwt_secret = settings.JWT_SECRET_KEY

    if supabase_secret and "placeholder" not in supabase_secret.lower() and supabase_secret != jwt_secret:
        try:
            payload = jwt.decode(
                token,
                supabase_secret,
                algorithms=["HS256"],
                options={"verify_signature": True, "verify_exp": True, "verify_aud": False},
            )
            # Token signature was cryptographically verified under SUPABASE_JWT_SECRET.
            # Requirement 2: For HS256 tokens signed using SUPABASE_JWT_SECRET, require the exact same issuer.
            # Requirement 4: Do not allow a token with a missing or incorrect issuer to fall through.
            if not expected_iss or payload.get("iss") != expected_iss:
                return None
            return payload
        except ExpiredSignatureError:
            return None
        except JWTError:
            pass
        except Exception:
            pass

    # Step 3: Attempt HS256 decode using internal JWT_SECRET_KEY
    if jwt_secret and "placeholder" not in jwt_secret.lower():
        try:
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],
                options={"verify_signature": True, "verify_exp": True, "verify_aud": False},
            )
            # Requirement 3: For internal ExamOps tokens signed using JWT_SECRET_KEY,
            # preserve compatibility with tokens that do not contain an issuer.
            token_iss = payload.get("iss")
            if token_iss is not None:
                # If an issuer is explicitly provided, it must match the expected issuer
                if expected_iss and token_iss != expected_iss:
                    return None
            return payload
        except (JWTError, ExpiredSignatureError):
            pass
        except Exception:
            pass

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
    payload = None

    if auth_header and auth_header.credentials:
        token = auth_header.credentials.strip()
        payload = verify_and_decode_jwt(token)
        if payload:
            user_id = payload.get("sub") or payload.get("id")
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired Bearer token signature.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    else:
        env = (settings.ENVIRONMENT or "").strip().lower()
        if env not in ("production", "prod"):
            # Internal test harness fallbacks allowed strictly in non-production test suites
            if x_test_user_id:
                user_id = x_test_user_id
            elif x_test_role:
                canonical_role = ROLE_ALIASES.get(x_test_role.upper(), x_test_role)
                cache_key = f"role:{canonical_role}"
                cached = _profile_cache.get(cache_key)
                if cached:
                    return cached

                prof = execute_query(
                    "SELECT * FROM user_profiles WHERE role = %s AND status = 'ACTIVE' ORDER BY created_at ASC LIMIT 1;",
                    (canonical_role,),
                    fetch_one=True,
                )
                if prof:
                    user = CurrentUser(
                        id=str(prof["id"]),
                        email=prof["email"],
                        display_name=prof["display_name"],
                        role=prof["role"],
                        student_id=str(prof["student_id"]) if prof["student_id"] else None,
                        invigilator_id=str(prof["invigilator_id"]) if prof["invigilator_id"] else None,
                        department=prof["department"],
                    )
                    _profile_cache.set(cache_key, user)
                    return user

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    cache_key = f"user:{user_id}"
    cached = _profile_cache.get(cache_key)
    if cached:
        return cached

    # Validate UUID syntax safely against PostgreSQL
    prof = None
    try:
        valid_uuid = str(uuid.UUID(str(user_id)))
        prof = execute_query(
            "SELECT * FROM user_profiles WHERE id = %s;",
            (valid_uuid,),
            fetch_one=True,
        )
    except (ValueError, TypeError, AttributeError):
        pass

    # Secondary lookup by email if token contains email
    if not prof and payload and payload.get("email"):
        prof = execute_query(
            "SELECT * FROM user_profiles WHERE LOWER(email) = %s;",
            (str(payload["email"]).strip().lower(),),
            fetch_one=True,
        )

    if not prof:
        raise HTTPException(
            status_code=401,
            detail=f"User profile not found for identifier '{user_id}'.",
        )

    if prof.get("status") != "ACTIVE":
        raise HTTPException(
            status_code=401,
            detail=f"User account '{prof['email']}' is inactive or suspended (status: {prof.get('status')}).",
        )

    user = CurrentUser(
        id=str(prof["id"]),
        email=prof["email"],
        display_name=prof["display_name"],
        role=prof["role"],
        student_id=str(prof["student_id"]) if prof.get("student_id") else None,
        invigilator_id=str(prof["invigilator_id"]) if prof.get("invigilator_id") else None,
        department=prof.get("department"),
    )
    _profile_cache.set(cache_key, user)
    return user

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
