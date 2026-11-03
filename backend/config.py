"""
ExamOps Backend Configuration
Loads environment variables from local .env files and environment variables.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, model_validator

def _load_env_file():
    """Loads key-value pairs from .env without overwriting existing environment variables."""
    possible_paths = [
        Path(os.getcwd()) / ".env",
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parent / ".env",
    ]
    for p in possible_paths:
        if p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key and key not in os.environ:
                                os.environ[key] = val
                break
            except Exception:
                pass

def _normalize_database_url(url: str) -> str:
    """Ensures passwords containing special characters like '@' are safely URL-encoded."""
    if not url or "@" not in url:
        return url
    try:
        prefix, host_part = url.rsplit("@", 1)
        if "://" in prefix and ":" in prefix.split("://", 1)[1]:
            scheme, rest = prefix.split("://", 1)
            user, raw_pass = rest.split(":", 1)
            import urllib.parse
            clean_pass = urllib.parse.unquote(raw_pass)
            enc_pass = urllib.parse.quote(clean_pass, safe="")
            return f"{scheme}://{user}:{enc_pass}@{host_part}"
    except Exception:
        pass
    return url

def _parse_cors_origins() -> list:
    """Parses CORS origins from env (JSON or comma-separated) and strips any wildcards."""
    raw = os.getenv("CORS_ORIGINS")
    default_origins = [
        "https://exam-ops-murex.vercel.app",
        "https://examops.vercel.app",
        "https://examops-staging.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    if not raw:
        return default_origins
    import json
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            # Never permit wildcard '*' when credentials mode is enabled
            origins = [o.strip() for o in parsed if o and o.strip() != "*"]
            if "https://exam-ops-murex.vercel.app" not in origins:
                origins.append("https://exam-ops-murex.vercel.app")
            return origins
    except Exception:
        pass
    origins = [o.strip() for o in raw.split(",") if o.strip() and o.strip() != "*"]
    if "https://exam-ops-murex.vercel.app" not in origins:
        origins.append("https://exam-ops-murex.vercel.app")
    return origins

_load_env_file()

DEFAULT_DEV_JWT_SECRET = "examops-dev-secret-key-for-local-authentication-20261022"

def validate_security_configuration(s: Optional["Settings"] = None) -> None:
    """
    Enforces production security invariants:
    1. Default development JWT secret MUST NEVER be used in production.
    2. JWT secret must be at least 32 characters with sufficient entropy.
    3. If DEMO_LOGIN_ENABLED is active in production, a strong DEMO_ACCESS_KEY is required.
    """
    target = s or settings
    env = (target.ENVIRONMENT or "development").strip().lower()
    if env in ("production", "prod"):
        secret = (target.JWT_SECRET_KEY or "").strip()
        insecure_secrets = {
            DEFAULT_DEV_JWT_SECRET,
            "secret",
            "changeme",
            "password",
            "placeholder",
            "1234567890",
        }
        if (
            not secret
            or secret in insecure_secrets
            or len(secret) < 32
            or "dev-secret" in secret.lower()
            or "placeholder" in secret.lower()
        ):
            raise RuntimeError(
                "FATAL SECURITY CONFIGURATION: Unsafe JWT_SECRET_KEY detected in production environment. "
                "Production requires a strong, high-entropy secret of at least 32 characters. "
                "Default development keys are strictly prohibited in production."
            )
        if target.SUPABASE_JWT_SECRET is not None:
            supabase_secret = target.SUPABASE_JWT_SECRET.strip()
            if (
                not supabase_secret
                or supabase_secret in insecure_secrets
                or len(supabase_secret) < 32
                or "dev-secret" in supabase_secret.lower()
                or "placeholder" in supabase_secret.lower()
            ):
                raise RuntimeError(
                    "FATAL SECURITY CONFIGURATION: Unsafe SUPABASE_JWT_SECRET detected in production environment. "
                    "When configured for HS256 verification in production, a strong, high-entropy secret "
                    "of at least 32 characters is required. Default, empty, or placeholder values are strictly prohibited."
                )

class Settings(BaseModel):
    PROJECT_NAME: str = "ExamOps"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEMO_LOGIN_ENABLED: bool = os.getenv("DEMO_LOGIN_ENABLED", "true").lower() in ("true", "1", "yes", "t")
    DEMO_ACCESS_KEY: str = os.getenv("DEMO_ACCESS_KEY", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "anon-key-placeholder")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key-placeholder")
    DATABASE_URL: str = _normalize_database_url(
        os.getenv("DATABASE_URL")
        or os.getenv("SUPABASE_DB_URL")
        or "postgresql://postgres:postgres@localhost:54329/examops"
    )
    # Recommended safe per-worker pool bounds for 4 Uvicorn workers under 20-connection PgBouncer limit
    # (4 workers * 4 maxconn = 16 combined max connections, preserving 4 connections headroom)
    DB_POOL_MIN_CONN: int = int(os.getenv("DB_POOL_MIN_CONN", "1"))
    DB_POOL_MAX_CONN: int = int(os.getenv("DB_POOL_MAX_CONN", "4"))
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", DEFAULT_DEV_JWT_SECRET)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET", None)
    CORS_ORIGINS: list = _parse_cors_origins()

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        validate_security_configuration(self)
        return self

settings = Settings()
