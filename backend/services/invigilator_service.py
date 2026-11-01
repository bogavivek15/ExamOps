"""
ExamOps Invigilator Management Service
"""
from typing import List, Dict, Optional, Any
from backend.database import execute_query, execute_mutation

class InvigilatorService:
    @staticmethod
    def list_invigilators(
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        department: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conditions = []
        params: List[Any] = []

        if search:
            conditions.append("(invigilator_code ILIKE %s OR first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s)")
            s = f"%{search}%"
            params.extend([s, s, s, s])
        if department:
            conditions.append("department = %s")
            params.append(department)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = f"""
        SELECT * FROM invigilators
        {where_clause}
        ORDER BY invigilator_code ASC
        LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return execute_query(sql, tuple(params))

    @staticmethod
    def get_invigilator_by_id(invigilator_id: str) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM invigilators WHERE id = %s;"
        return execute_query(sql, (invigilator_id,), fetch_one=True)

    @staticmethod
    def get_invigilator_availabilities(invigilator_id: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM availabilities WHERE invigilator_id = %s ORDER BY day_of_week ASC, start_time ASC;"
        return execute_query(sql, (invigilator_id,))

    @staticmethod
    def get_invigilator_assignments(invigilator_id: str) -> List[Dict[str, Any]]:
        sql = """
        SELECT ai.id as assignment_invigilator_id, ai.role as invigilator_role,
               sa.id as assignment_id, sa.assignment_code, sa.start_time, sa.end_time, sa.status as assignment_status,
               ex.id as exam_id, ex.exam_code, ex.title as exam_title,
               r.id as room_id, r.room_code, r.name as room_name, r.building
        FROM assignment_invigilators ai
        JOIN schedule_assignments sa ON sa.id = ai.assignment_id
        JOIN exams ex ON ex.id = sa.exam_id
        JOIN rooms r ON r.id = sa.room_id
        WHERE ai.invigilator_id = %s
        ORDER BY sa.start_time ASC;
        """
        return execute_query(sql, (invigilator_id,))
