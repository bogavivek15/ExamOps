"""
ExamOps Room & Resource Management Service
"""
from typing import List, Dict, Optional, Any
from backend.database import execute_query, execute_mutation

class RoomService:
    @staticmethod
    def list_rooms(
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        building: Optional[str] = None,
        floor: Optional[int] = None,
        is_accessible: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        conditions = []
        params: List[Any] = []

        if search:
            conditions.append("(r.room_code ILIKE %s OR r.name ILIKE %s OR r.building ILIKE %s)")
            s = f"%{search}%"
            params.extend([s, s, s])
        if building:
            conditions.append("r.building = %s")
            params.append(building)
        if floor is not None:
            conditions.append("r.floor = %s")
            params.append(floor)
        if is_accessible is not None:
            conditions.append("r.is_accessible = %s")
            params.append(is_accessible)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = f"""
        SELECT r.*,
               rc.standard_capacity,
               rc.exam_capacity
        FROM rooms r
        LEFT JOIN room_capacities rc ON rc.room_id = r.id AND CURRENT_DATE BETWEEN rc.effective_start AND rc.effective_end
        {where_clause}
        ORDER BY r.room_code ASC
        LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return execute_query(sql, tuple(params))

    @staticmethod
    def get_room_by_id(room_id: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT r.*,
               rc.standard_capacity,
               rc.exam_capacity
        FROM rooms r
        LEFT JOIN room_capacities rc ON rc.room_id = r.id AND CURRENT_DATE BETWEEN rc.effective_start AND rc.effective_end
        WHERE r.id = %s;
        """
        return execute_query(sql, (room_id,), fetch_one=True)

    @staticmethod
    def get_room_capacities(room_id: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM room_capacities WHERE room_id = %s ORDER BY effective_start DESC;"
        return execute_query(sql, (room_id,))

    @staticmethod
    def get_room_equipment(room_id: str) -> List[Dict[str, Any]]:
        sql = """
        SELECT re.*, et.code as type_code, et.name as equipment_name, et.category
        FROM room_equipment re
        JOIN equipment_types et ON et.id = re.equipment_type_id
        WHERE re.room_id = %s;
        """
        return execute_query(sql, (room_id,))

    @staticmethod
    def get_room_availabilities(room_id: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM room_availabilities WHERE room_id = %s ORDER BY effective_start ASC;"
        return execute_query(sql, (room_id,))
