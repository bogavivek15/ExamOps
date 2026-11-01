"""
ExamOps Audit & Activity Log Routes
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any, Optional
from backend.auth import get_current_user, CurrentUser, require_roles
from backend.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit & Activity"])

@router.get("/logs", dependencies=[Depends(require_roles("ACADEMIC_ADMINISTRATOR", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN"))])
def list_audit_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves immutable audit logs showing user actions, state changes, and results."""
    return AuditService.list_logs(limit=limit, offset=offset, entity_type=entity_type, action=action)

