"""
ExamOps Export Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Dict, Any
from backend.auth import get_current_user, CurrentUser
from backend.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["Exports"])

@router.get("/runs/{run_id}/csv")
def export_run_csv(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Exports confirmed examination timetable assignments as a CSV file."""
    csv_content = ExportService.export_schedule_csv(run_id)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=examops_schedule_{run_id[:8]}.csv"},
    )

@router.get("/runs/{run_id}/json")
def export_run_json(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Exports complete scheduling run data including telemetry as JSON."""
    return ExportService.export_schedule_json(run_id)
