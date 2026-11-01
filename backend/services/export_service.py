"""
ExamOps Export Service
Exports scheduling runs, assignments, student seatings, and metrics to CSV and JSON formats.
"""
from typing import Dict, Any, List
import io
import csv
import json
from backend.database import execute_query

class ExportService:
    @staticmethod
    def export_schedule_csv(run_id: str) -> str:
        """Generates a CSV string containing all confirmed assignments in a scheduling run."""
        sql = """
        SELECT sa.assignment_code,
               ex.exam_code,
               ex.title as exam_title,
               c.course_code,
               r.room_code,
               r.name as room_name,
               r.building,
               sa.start_time,
               sa.end_time,
               sa.status,
               (SELECT count(*) FROM assignment_students ast WHERE ast.assignment_id = sa.id) as seated_students,
               (SELECT string_agg(i.invigilator_code, '; ')
                FROM assignment_invigilators ai
                JOIN invigilators i ON i.id = ai.invigilator_id
                WHERE ai.assignment_id = sa.id) as assigned_invigilators
        FROM schedule_assignments sa
        JOIN exams ex ON ex.id = sa.exam_id
        JOIN courses c ON c.id = ex.course_id
        JOIN rooms r ON r.id = sa.room_id
        WHERE sa.scheduling_run_id = %s
        ORDER BY sa.start_time ASC, ex.exam_code ASC;
        """
        rows = execute_query(sql, (run_id,))

        output = io.StringIO()
        if not rows:
            return "No assignments found for this scheduling run.\n"

        fieldnames = [
            "assignment_code",
            "exam_code",
            "exam_title",
            "course_code",
            "room_code",
            "room_name",
            "building",
            "start_time",
            "end_time",
            "status",
            "seated_students",
            "assigned_invigilators",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

        return output.getvalue()

    @staticmethod
    def export_schedule_json(run_id: str) -> Dict[str, Any]:
        """Generates a full JSON document with run details, metrics, assignments, and decisions."""
        run = execute_query("SELECT * FROM scheduling_runs WHERE id = %s;", (run_id,), fetch_one=True)
        if not run:
            return {"error": "Run not found"}

        assignments = execute_query(
            """
            SELECT sa.*, ex.exam_code, ex.title as exam_title, r.room_code, r.name as room_name
            FROM schedule_assignments sa
            JOIN exams ex ON ex.id = sa.exam_id
            JOIN rooms r ON r.id = sa.room_id
            WHERE sa.scheduling_run_id = %s
            ORDER BY sa.start_time ASC;
            """,
            (run_id,),
        )

        decisions = execute_query(
            """
            SELECT sd.*, ex.exam_code 
            FROM scheduling_decisions sd
            JOIN exams ex ON ex.id = sd.exam_id
            WHERE sd.scheduling_run_id = %s
            ORDER BY sd.decision_order ASC;
            """,
            (run_id,),
        )

        return {
            "scheduling_run": run,
            "total_assignments": len(assignments),
            "assignments": assignments,
            "decisions": decisions,
        }
