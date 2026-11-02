"""
ExamOps Backend Application Entry Point
FastAPI + Pydantic + Supabase PostgreSQL
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from contextlib import asynccontextmanager
import time

from backend.config import settings
from backend.database import execute_query, init_db_pool

# Import route modules
from backend.routes.auth_routes import router as auth_router
from backend.routes.student_routes import router as student_router
from backend.routes.course_routes import router as course_router
from backend.routes.exam_routes import router as exam_router
from backend.routes.room_routes import router as room_router
from backend.routes.invigilator_routes import router as invigilator_router
from backend.routes.accommodation_routes import router as accommodation_router
from backend.routes.scheduling_routes import router as scheduling_router
from backend.routes.analytics_routes import router as analytics_router
from backend.routes.audit_routes import router as audit_router
from backend.routes.export_routes import router as export_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_pool()
    yield

app = FastAPI(
    title="ExamOps API",
    description="Examination Operations & Intelligent Scheduling Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Convenient redirects for /api/docs, /api/openapi.json, and /api/redoc
@app.get("/api/docs", include_in_schema=False)
def redirect_api_docs():
    return RedirectResponse(url="/docs")

@app.get("/api/openapi.json", include_in_schema=False)
def redirect_api_openapi():
    return RedirectResponse(url="/openapi.json")

@app.get("/api/redoc", include_in_schema=False)
def redirect_api_redoc():
    return RedirectResponse(url="/redoc")

# GZip Compression Middleware (compresses responses > 1KB)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Process-Time"],
)

@app.middleware("http")
async def add_security_and_timing_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint confirming API service and database connectivity."""
    db_status = "UNKNOWN"
    try:
        res = execute_query("SELECT 1 as healthy;", fetch_one=True)
        if res and res.get("healthy") == 1:
            db_status = "HEALTHY"
    except Exception as e:
        db_status = f"UNHEALTHY: {str(e)}"

    return {
        "status": "ONLINE",
        "service": "ExamOps Backend",
        "version": settings.VERSION,
        "database": db_status,
    }

# Register all API routers under /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(student_router, prefix="/api")
app.include_router(course_router, prefix="/api")
app.include_router(exam_router, prefix="/api")
app.include_router(room_router, prefix="/api")
app.include_router(invigilator_router, prefix="/api")
app.include_router(accommodation_router, prefix="/api")
app.include_router(scheduling_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(export_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

