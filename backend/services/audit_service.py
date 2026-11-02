"""
ExamOps Audit Log Service
Tracks authoritative state changes, approvals, publications, and security access events.
"""
from typing import List, Dict, Optional, Any
import json
from backend.database import execute_query, execute_mutation

class AuditService:
    @staticmethod
    def log_event(
        user_id: Optional[str],
        user_role: Optional[str],
        action: str,
        entity_type: str,
        entity_id: str,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        result: str = "SUCCESS",
    ) -> None:
        """Inserts an immutable audit log entry."""
        sql = """
        INSERT INTO audit_logs (
            user_id, user_role, action, entity_type, entity_id,
            previous_state, new_state, result
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        execute_mutation(
            sql,
            (
                user_id,
                user_role,
                action,
                entity_type,
                entity_id,
                json.dumps(previous_state, default=str) if previous_state else None,
                json.dumps(new_state, default=str) if new_state else None,
                result,
            ),
        )

    @staticmethod
    def list_logs(
        limit: int = 100,
        offset: int = 0,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conditions = []
        params: List[Any] = []

        if entity_type:
            clean_et = entity_type.strip().lower()
            singular = clean_et[:-1] if clean_et.endswith('s') else clean_et
            plural = clean_et if clean_et.endswith('s') else f"{clean_et}s"
            conditions.append("(LOWER(al.entity_type) = %s OR LOWER(al.entity_type) = %s OR al.entity_type ILIKE %s)")
            params.extend([singular, plural, f"%{singular}%"])
        if action:
            clean_act = action.strip()
            conditions.append("(al.action ILIKE %s OR al.action ILIKE %s)")
            params.extend([clean_act, f"%{clean_act.replace('RUN', 'SCHEDULING_RUN')}%"])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = f"""
        SELECT al.*, up.email, up.display_name
        FROM audit_logs al
        LEFT JOIN user_profiles up ON up.id = al.user_id
        {where_clause}
        ORDER BY al.created_at DESC
        LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return execute_query(sql, tuple(params))
