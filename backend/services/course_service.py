"""
ExamOps Course & Examination Domain Services
"""
from typing import List, Dict, Optional, Any
from backend.database import execute_query, execute_mutation

class CourseService:
    @staticmethod
    def list_courses(limit: int = 100, offset: int = 0, department: Optional[str] = None) -> List[Dict[str, Any]]:
        if department:
            sql = "SELECT * FROM courses WHERE department = %s ORDER BY course_code ASC LIMIT %s OFFSET %s;"
            return execute_query(sql, (department, limit, offset))
        return execute_query("SELECT * FROM courses ORDER BY course_code ASC LIMIT %s OFFSET %s;", (limit, offset))

    @staticmethod
    def get_course_by_id(course_id: str) -> Optional[Dict[str, Any]]:
        return execute_query("SELECT * FROM courses WHERE id = %s;", (course_id,), fetch_one=True)

    @staticmethod
    def list_enrollments(course_id: Optional[str] = None, student_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if course_id:
            sql = "SELECT * FROM enrollments WHERE course_id = %s LIMIT %s;"
            return execute_query(sql, (course_id, limit))
        if student_id:
            sql = "SELECT * FROM enrollments WHERE student_id = %s LIMIT %s;"
            return execute_query(sql, (student_id, limit))
        return execute_query("SELECT * FROM enrollments LIMIT %s;", (limit,))

class ExamService:
    @staticmethod
    def list_exams(limit: int = 100, offset: int = 0, status: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT ex.*, c.name as course_name, c.course_code,
               (SELECT count(*) FROM enrollments enr WHERE enr.course_id = ex.course_id AND enr.status = 'ACTIVE') as enrolled_student_count
        FROM exams ex
        JOIN courses c ON c.id = ex.course_id
        """
        if status:
            sql += " WHERE ex.status = %s ORDER BY ex.exam_code ASC LIMIT %s OFFSET %s;"
            return execute_query(sql, (status, limit, offset))
        sql += " ORDER BY ex.exam_code ASC LIMIT %s OFFSET %s;"
        return execute_query(sql, (limit, offset))

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
