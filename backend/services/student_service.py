"""
ExamOps Student Management Service
"""
from typing import List, Dict, Optional, Any
from backend.database import execute_query, execute_mutation

class StudentService:
    @staticmethod
    def list_students(limit: int = 100, offset: int = 0, search: Optional[str] = None) -> List[Dict[str, Any]]:
        if search:
            sql = """
            SELECT * FROM students 
            WHERE student_code ILIKE %s OR first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s
            ORDER BY student_code ASC LIMIT %s OFFSET %s;
            """
            s = f"%{search}%"
            return execute_query(sql, (s, s, s, s, limit, offset))
        return execute_query(
            "SELECT * FROM students ORDER BY student_code ASC LIMIT %s OFFSET %s;",
            (limit, offset),
        )

    @staticmethod
    def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
        return execute_query(
            "SELECT * FROM students WHERE id = %s;",
            (student_id,),
            fetch_one=True,
        )

    @staticmethod
    def get_student_enrollments(student_id: str) -> List[Dict[str, Any]]:
        sql = """
        SELECT e.*, c.course_code, c.name as course_name, c.department
        FROM enrollments e
        JOIN courses c ON c.id = e.course_id
        WHERE e.student_id = %s
        ORDER BY c.course_code ASC;
        """
        return execute_query(sql, (student_id,))

    @staticmethod
    def get_student_schedule(student_id: str) -> List[Dict[str, Any]]:
        sql = """
        SELECT ast.id as assignment_student_id, ast.effective_duration_minutes, ast.start_time, ast.end_time,
               sa.assignment_code, sa.status as assignment_status,
               ex.id as exam_id, ex.exam_code, ex.title as exam_title,
               r.id as room_id, r.room_code, r.name as room_name, r.building, r.floor, r.is_accessible
        FROM assignment_students ast
        JOIN schedule_assignments sa ON sa.id = ast.assignment_id
        JOIN exams ex ON ex.id = ast.exam_id
        JOIN rooms r ON r.id = ast.room_id
        WHERE ast.student_id = %s
        ORDER BY ast.start_time ASC;
        """
        return execute_query(sql, (student_id,))
