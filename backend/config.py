"""
ExamOps Backend Configuration
"""
import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "ExamOps"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "anon-key-placeholder")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key-placeholder")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54329/examops")
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
