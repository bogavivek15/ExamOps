"""
ExamOps Scheduling Engine & Operational Workspace Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional, Set
import threading
from pydantic import BaseModel
from backend.auth import get_current_user, CurrentUser, require_roles
from backend.services.scheduling_service import SchedulingService
from backend.services.audit_service import AuditService
from backend.services.distributed_lock import distributed_advisory_lock, DistributedLockConflictError

router = APIRouter(prefix="/scheduling", tags=["Scheduling Operations"])

class CreateRunRequest(BaseModel):
    academic_period_id: str
    algorithm_version: str = "1.0.0"
    seed: int = 20261022
    auto_execute: bool = False

@router.get("/runs")
def list_scheduling_runs(
    academic_period_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists all scheduling runs with status, execution counts, and creator metadata.
    Learners and Instructors are restricted strictly to PUBLISHED runs."""
    runs = SchedulingService.list_runs(academic_period_id=academic_period_id, limit=limit, offset=offset)
    if current_user.role in ("LEARNER", "STUDENT", "INSTRUCTOR"):
        return [r for r in runs if r.get("status") == "PUBLISHED"]
    return runs

@router.post("/runs", dependencies=[Depends(require_roles("ACADEMIC_ADMINISTRATOR", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN", "EXAM_OFFICER"))])
def create_scheduling_run(
    req: CreateRunRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Creates a new scheduling run. If auto_execute is True, immediately solves and allocates rooms/invigilators."""
    run = SchedulingService.create_scheduling_run(
        academic_period_id=req.academic_period_id,
        created_by=current_user.id,
        algorithm_version=req.algorithm_version,
        seed=req.seed,
    )
    AuditService.log_event(
        user_id=current_user.id,
        user_role=current_user.role,
        action="CREATE_SCHEDULING_RUN",
        entity_type="scheduling_runs",
        entity_id=run.get("id", ""),
        new_state=run,
    )

    if req.auto_execute:
        with distributed_advisory_lock(run["id"]):
            exec_result = SchedulingService.execute_scheduling_run(run["id"])
            run = SchedulingService.get_run_by_id(run["id"])
            AuditService.log_event(
                user_id=current_user.id,
                user_role=current_user.role,
                action="EXECUTE_SCHEDULING_RUN",
                entity_type="scheduling_runs",
                entity_id=run["id"],
                new_state=exec_result,
            )

    return run

@router.get("/runs/{run_id}")
def get_scheduling_run(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves detailed status and progress of a scheduling run."""
    run = SchedulingService.get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Scheduling run not found")
    if current_user.role in ("LEARNER", "STUDENT", "INSTRUCTOR") and run.get("status") != "PUBLISHED":
        raise HTTPException(status_code=403, detail="Forbidden: Unreleased timetable drafts are restricted to operations staff.")
    return run

@router.post("/runs/{run_id}/execute", dependencies=[Depends(require_roles("ACADEMIC_ADMINISTRATOR", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN", "EXAM_OFFICER"))])
def execute_scheduling_run(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Executes the deterministic scheduling solver for this run.
    Freezes student snapshots, checks conflict graph, solves room & invigilator allocations,
    performs independent validation, and commits assignments and telemetry.
    Uses PostgreSQL-backed distributed advisory locks for multi-worker and multi-process safety.
    """
    run = SchedulingService.get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Scheduling run '{run_id}' not found.")
    if run.get("status") == "PUBLISHED":
        raise HTTPException(
            status_code=400,
            detail=f"Scheduling run '{run_id}' is already PUBLISHED and cannot be re-executed. Create a new scheduling run to generate a new timetable.",
        )

    try:
        with distributed_advisory_lock(run_id):
            result = SchedulingService.execute_scheduling_run(run_id)
            AuditService.log_event(
                user_id=current_user.id,
                user_role=current_user.role,
                action="EXECUTE_SCHEDULING_RUN",
                entity_type="scheduling_runs",
                entity_id=run_id,
                new_state=result,
            )
            return result
    except DistributedLockConflictError:
        raise HTTPException(
            status_code=409,
            detail=f"Scheduling run '{run_id}' is already actively executing on another worker. Please wait for completion.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        AuditService.log_event(
            user_id=current_user.id,
            user_role=current_user.role,
            action="EXECUTE_SCHEDULING_RUN",
            entity_type="scheduling_runs",
            entity_id=run_id,
            result="FAILURE",
            new_state={"error": str(e)},
        )
        raise HTTPException(status_code=500, detail=f"Scheduling execution failed: {str(e)}")

@router.get("/runs/{run_id}/assignments")
def get_run_assignments(
    run_id: str,
    exam_id: Optional[str] = None,
    room_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves confirmed room and timetable assignments for a run."""
    if current_user.role in ("LEARNER", "STUDENT"):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Learners cannot inspect institutional assignment tables. Please access your personal schedule via /api/students/{student_id}/schedule.",
        )
    return SchedulingService.get_run_assignments(
        run_id=run_id,
        exam_id=exam_id,
        room_id=room_id,
        limit=limit,
        offset=offset,
    )

@router.get("/runs/{run_id}/decisions", dependencies=[Depends(require_roles("ACADEMIC_ADMINISTRATOR", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN", "EXAM_OFFICER"))])
def get_run_decisions(
    run_id: str,
    exam_id: Optional[str] = None,
    is_assigned: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves full algorithm telemetry: why each exam was scheduled or unassigned."""
    return SchedulingService.get_run_decisions(
        run_id=run_id,
        exam_id=exam_id,
        is_assigned=is_assigned,
        limit=limit,
        offset=offset,
    )

@router.get("/runs/{run_id}/issues", dependencies=[Depends(require_roles("SUPPORT_STAFF", "ACADEMIC_ADMINISTRATOR", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN", "EXAM_OFFICER", "INVIGILATOR"))])
def get_run_validation_issues(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves validation issues and constraint checks for a scheduling run."""
    return SchedulingService.get_run_validation_issues(run_id)

@router.post("/runs/{run_id}/approve", dependencies=[Depends(require_roles("ACADEMIC_ADMINISTRATOR", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN"))])
def approve_scheduling_run(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Approves a completed run prior to official publication."""
    try:
        res = SchedulingService.approve_run(run_id, current_user.id)
        AuditService.log_event(
            user_id=current_user.id,
            user_role=current_user.role,
            action="APPROVE_SCHEDULE",
            entity_type="scheduling_runs",
            entity_id=run_id,
            new_state=res,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/runs/{run_id}/publish", dependencies=[Depends(require_roles("ACADEMIC_ADMINISTRATOR", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN"))])
def publish_scheduling_run(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Atomically publishes a scheduling run using row locks on the academic period.
    Supersedes any previously published schedule.
    Uses PostgreSQL distributed advisory lock to guarantee consistency with ongoing execution.
    """
    try:
        run = SchedulingService.get_run_by_id(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Scheduling run '{run_id}' not found.")

        # Idempotent: If run is already published, return success immediately
        if run.get("status") == "PUBLISHED":
            return {
                "success": True,
                "published_run_id": run_id,
                "status": "PUBLISHED",
                "message": f"Timetable '{run.get('run_code', run_id)}' is already officially published and immutable.",
            }

        if run.get("status") == "SUPERSEDED":
            raise HTTPException(
                status_code=400,
                detail=f"Timetable '{run.get('run_code', run_id)}' has been superseded by a newer published schedule and cannot be published. Please create a new timetable draft.",
            )

        if run.get("status") == "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail=f"Timetable '{run.get('run_code', run_id)}' is cancelled and cannot be published. Please create a new timetable draft.",
            )

        with distributed_advisory_lock(run_id):
            res = SchedulingService.publish_run(run_id, current_user.id)
            return res
    except DistributedLockConflictError:
        raise HTTPException(
            status_code=409,
            detail=f"Scheduling run '{run_id}' is actively being processed on another worker.",
        )
    except HTTPException:
        raise
    except Exception as e:
        # Strip PostgreSQL context if present to avoid leaking raw PL/pgSQL internals
        raw_msg = str(e).split("\nCONTEXT:")[0].strip()
        clean_msg = raw_msg.replace("Publication failed: ", "").strip()
        raise HTTPException(status_code=400, detail=clean_msg)

