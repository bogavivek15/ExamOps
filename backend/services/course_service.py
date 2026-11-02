"""
ExamOps Course & Examination Domain Services
"""
from typing import List, Dict, Optional, Any
from backend.database import execute_query, execute_mutation

class CourseService:
    @staticmethod
    def list_courses(limit: int = 100, offset: int = 0, department: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        conditions = []
        params = []
        if department:
            conditions.append("c.department = %s")
            params.append(department)
        if search:
            conditions.append("(c.course_code ILIKE %s OR c.name ILIKE %s OR c.department ILIKE %s)")
            s = f"%{search}%"
            params.extend([s, s, s])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"""
        SELECT c.*,
               (SELECT count(*) FROM enrollments e WHERE e.course_id = c.id) as enrolled_count
        FROM courses c
        {where_clause}
        ORDER BY c.course_code ASC
        LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return execute_query(sql, tuple(params))

    @staticmethod
    def get_course_by_id(course_id: str) -> Optional[Dict[str, Any]]:
        return execute_query("SELECT * FROM courses WHERE id = %s;", (course_id,), fetch_one=True)

    @staticmethod
    def list_enrollments(course_id: Optional[str] = None, student_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if course_id:
            sql = """
            SELECT e.*, s.student_code, s.student_code as student_number,
                   concat(s.first_name, ' ', s.last_name) as student_name,
                   e.status as enrollment_status
            FROM enrollments e
            JOIN students s ON s.id = e.student_id
            WHERE e.course_id = %s
            ORDER BY s.student_code ASC
            LIMIT %s;
            """
            return execute_query(sql, (course_id, limit))
        if student_id:
            sql = "SELECT * FROM enrollments WHERE student_id = %s LIMIT %s;"
            return execute_query(sql, (student_id, limit))
        return execute_query("SELECT * FROM enrollments LIMIT %s;", (limit,))

class ExamService:
    @staticmethod
    def list_exams(limit: int = 100, offset: int = 0, status: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT ex.*, c.name as course_name, c.course_code,
               (SELECT count(*) FROM enrollments enr WHERE enr.course_id = ex.course_id AND enr.status = 'ACTIVE') as enrolled_student_count
        FROM exams ex
        JOIN courses c ON c.id = ex.course_id
        WHERE 1=1
        """
        params = []
        if status:
            sql += " AND ex.status = %s"
            params.append(status)
        if search:
            sql += " AND (ex.exam_code ILIKE %s OR ex.title ILIKE %s OR c.course_code ILIKE %s)"
            s = f"%{search}%"
            params.extend([s, s, s])
        sql += " ORDER BY ex.exam_code ASC LIMIT %s OFFSET %s;"
        params.extend([limit, offset])
        return execute_query(sql, tuple(params))

    @staticmethod
    def get_exam_by_id(exam_id: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT ex.*, c.name as course_name, c.course_code,
               (SELECT count(*) FROM enrollments enr WHERE enr.course_id = ex.course_id AND enr.status = 'ACTIVE') as enrolled_student_count
        FROM exams ex
        JOIN courses c ON c.id = ex.course_id
        WHERE ex.id = %s;
        """
        return execute_query(sql, (exam_id,), fetch_one=True)

    @staticmethod
    def get_exam_requirements(exam_id: str) -> List[Dict[str, Any]]:
        return execute_query("SELECT * FROM exam_requirements WHERE exam_id = %s;", (exam_id,))

