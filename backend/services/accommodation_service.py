"""
ExamOps Accommodation Service with Medical Privacy Redaction
"""
from typing import List, Dict, Optional, Any
from backend.database import execute_query, execute_mutation

class AccommodationService:
    @staticmethod
    def list_accommodations(
        limit: int = 100,
        offset: int = 0,
        student_id: Optional[str] = None,
        accommodation_type: Optional[str] = None,
        active_only: bool = False,
    ) -> List[Dict[str, Any]]:
        conditions = []
        params: List[Any] = []

        if student_id:
            conditions.append("a.student_id = %s")
            params.append(student_id)
        if accommodation_type:
            conditions.append("a.accommodation_type = %s")
            params.append(accommodation_type)
        if active_only:
            conditions.append("a.is_active = TRUE AND CURRENT_DATE BETWEEN a.effective_start AND a.effective_end")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = f"""
        SELECT a.*,
               s.student_code, s.first_name, s.last_name, s.program
        FROM accommodations a
        JOIN students s ON s.id = a.student_id
        {where_clause}
        ORDER BY s.student_code ASC, a.accommodation_code ASC
        LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return execute_query(sql, tuple(params))

    @staticmethod
    def get_accommodation_by_id(acc_id: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT a.*,
               s.student_code, s.first_name, s.last_name, s.program
        FROM accommodations a
        JOIN students s ON s.id = a.student_id
        WHERE a.id = %s;
        """
        return execute_query(sql, (acc_id,), fetch_one=True)

    @staticmethod
    def get_accommodation_notes(acc_id: str, viewer_role: str) -> List[Dict[str, Any]]:
        """
        Retrieves accommodation clinical notes.
        Masks medical details unless the viewer has SUPER_ADMIN, EXAM_OFFICER,
        ACADEMIC_ADMINISTRATOR, or PLATFORM_ADMINISTRATOR permissions.
        """
        sql = "SELECT * FROM accommodation_notes WHERE accommodation_id = %s;"
        notes = execute_query(sql, (acc_id,))

        allowed_roles = {
            "SUPER_ADMIN",
            "EXAM_OFFICER",
            "ACADEMIC_ADMINISTRATOR",
            "PLATFORM_ADMINISTRATOR",
        }
        if viewer_role in allowed_roles:
            return notes

        # Redact medical privacy fields for unauthorized roles
        redacted_notes = []
        for note in notes:
            note_copy = dict(note)
            note_copy["clinical_notes"] = "[CONFIDENTIAL CLINICAL RECORD REDACTED - AUTHORIZED ACCESS ONLY]"
            if note_copy.get("documentation_url"):
                note_copy["documentation_url"] = "[REDACTED]"
            redacted_notes.append(note_copy)
        return redacted_notes
