"""
ExamOps Backend Configuration
Loads environment variables from local .env files and environment variables.
"""
import os
from pathlib import Path
from pydantic import BaseModel

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

_load_env_file()

class Settings(BaseModel):
    PROJECT_NAME: str = "ExamOps"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "anon-key-placeholder")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key-placeholder")
    DATABASE_URL: str = _normalize_database_url(
        os.getenv("DATABASE_URL")
        or os.getenv("SUPABASE_DB_URL")
        or "postgresql://postgres:postgres@localhost:54329/examops"
    )
    DB_POOL_MIN_CONN: int = int(os.getenv("DB_POOL_MIN_CONN", "2"))
    DB_POOL_MAX_CONN: int = int(os.getenv("DB_POOL_MAX_CONN", "20"))
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "examops-dev-secret-key-for-local-authentication-20261022")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://examops.vercel.app",
        "*",
    ]

settings = Settings()
