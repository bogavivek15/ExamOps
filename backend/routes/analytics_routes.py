"""
ExamOps Analytics & Reconciliation Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from backend.auth import get_current_user, CurrentUser
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Telemetry"])

@router.get("/overview")
def get_analytics_overview(current_user: CurrentUser = Depends(get_current_user)):
    """Returns high-level institution operational metrics and capacity statistics."""
    return AnalyticsService.get_overview_metrics()

@router.get("/runs/{run_id}/reconciliation")
def get_run_reconciliation(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Returns mathematical reconciliation and distribution metrics for a scheduling run."""
    recon = AnalyticsService.get_run_reconciliation(run_id)
    if not recon:
        raise HTTPException(status_code=404, detail="Run not found")
    return recon

