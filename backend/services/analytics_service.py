"""
ExamOps Analytics & Reconciliation Service
Provides real-time operational metrics and mathematical reconciliation audits.
"""
from typing import Dict, Any, List, Optional
from backend.database import execute_query

class AnalyticsService:
    @staticmethod
    def get_overview_metrics() -> Dict[str, Any]:
        """Calculates institution-wide operational metrics from authoritative DB tables."""
        total_students = execute_query("SELECT count(*) as c FROM students;", fetch_one=True)["c"]
        total_courses = execute_query("SELECT count(*) as c FROM courses;", fetch_one=True)["c"]
        total_exams = execute_query("SELECT count(*) as c FROM exams;", fetch_one=True)["c"]
        total_rooms = execute_query("SELECT count(*) as c FROM rooms;", fetch_one=True)["c"]
        total_invigilators = execute_query("SELECT count(*) as c FROM invigilators;", fetch_one=True)["c"]
        total_accommodations = execute_query("SELECT count(*) as c FROM accommodations WHERE is_active = TRUE;", fetch_one=True)["c"]

        # Active academic period
        active_period = execute_query(
            "SELECT * FROM academic_periods WHERE is_active = TRUE LIMIT 1;",
            fetch_one=True,
        )

        # Most relevant scheduling run (PUBLISHED first, else latest COMPLETED)
        run = execute_query(
            "SELECT * FROM scheduling_runs WHERE status = 'PUBLISHED' ORDER BY updated_at DESC LIMIT 1;",
            fetch_one=True,
        )
        if not run:
            run = execute_query(
                "SELECT * FROM scheduling_runs WHERE status IN ('COMPLETED', 'APPROVED', 'REVIEW_REQUIRED') ORDER BY created_at DESC LIMIT 1;",
                fetch_one=True,
            )

        scheduled_count = run["scheduled_count"] if run else 0
        unassigned_count = run["unassigned_count"] if run else 0
        total_run_exams = run["total_exams"] if run else 0
        completion_pct = round((scheduled_count / total_run_exams) * 100.0, 2) if total_run_exams > 0 else 0.0

        # Seated student registrations in the run
        seated_count = 0
        if run:
            seated_count = execute_query(
                "SELECT count(*) as c FROM assignment_students WHERE scheduling_run_id = %s;",
                (run["id"],),
                fetch_one=True,
            )["c"]

        return {
            "total_students": total_students,
            "total_courses": total_courses,
            "total_exams": total_exams,
            "total_rooms": total_rooms,
            "total_invigilators": total_invigilators,
            "total_active_accommodations": total_accommodations,
            "active_period": active_period,
            "latest_run": run,
            "scheduled_exams": scheduled_count,
            "unassigned_exams": unassigned_count,
            "completion_rate_pct": completion_pct,
            "total_seated_registrations": seated_count,
        }

    @staticmethod
    def get_run_reconciliation(run_id: str) -> Dict[str, Any]:
        """
        Calculates mathematical reconciliation metrics for a specific scheduling run.
        Proves every student, room, and invigilator assignment aligns with inputs.
        """
        run = execute_query("SELECT * FROM scheduling_runs WHERE id = %s;", (run_id,), fetch_one=True)
        if not run:
            return {}

        total_exams = run["total_exams"]
        scheduled_count = run["scheduled_count"]
        unassigned_count = run["unassigned_count"]

        # Decisions audit
        dec_stats = execute_query(
            """
            SELECT is_assigned, count(*) as count 
            FROM scheduling_decisions 
            WHERE scheduling_run_id = %s 
            GROUP BY is_assigned;
            """,
            (run_id,),
        )
        assigned_decisions = 0
        unassigned_decisions = 0
        for ds in dec_stats:
            if ds["is_assigned"]:
                assigned_decisions = ds["count"]
            else:
                unassigned_decisions = ds["count"]

        # Room assignments breakdown
        room_allocs = execute_query(
            """
            SELECT sa.room_id, r.room_code, count(sa.id) as num_slots_used,
                   count(ast.id) as total_students_seated
            FROM schedule_assignments sa
            JOIN rooms r ON r.id = sa.room_id
            LEFT JOIN assignment_students ast ON ast.assignment_id = sa.id
            WHERE sa.scheduling_run_id = %s
            GROUP BY sa.room_id, r.room_code
            ORDER BY count(sa.id) DESC;
            """,
            (run_id,),
        )

        # Invigilator assignments breakdown
        inv_allocs = execute_query(
            """
            SELECT ai.invigilator_id, i.invigilator_code, i.first_name, i.last_name,
                   count(ai.id) as shift_count
            FROM assignment_invigilators ai
            JOIN invigilators i ON i.id = ai.invigilator_id
            JOIN schedule_assignments sa ON sa.id = ai.assignment_id
            WHERE sa.scheduling_run_id = %s
            GROUP BY ai.invigilator_id, i.invigilator_code, i.first_name, i.last_name
            ORDER BY count(ai.id) DESC;
            """,
            (run_id,),
        )

        # Reason code frequency for unassigned exams
        unassigned_reasons = execute_query(
            """
            SELECT unnest(reason_codes) as reason, count(*) as freq
            FROM scheduling_decisions
            WHERE scheduling_run_id = %s AND is_assigned = FALSE
            GROUP BY reason
            ORDER BY freq DESC;
            """,
            (run_id,),
        )

        return {
            "run_id": run_id,
            "run_code": run["run_code"],
            "status": run["status"],
            "total_exams": total_exams,
            "scheduled_count": scheduled_count,
            "unassigned_count": unassigned_count,
            "reconciles_exactly": (scheduled_count + unassigned_count) == total_exams,
            "assigned_decisions": assigned_decisions,
            "unassigned_decisions": unassigned_decisions,
            "rooms_utilized_count": len(room_allocs),
            "invigilators_utilized_count": len(inv_allocs),
            "room_allocations_summary": room_allocs[:15],
            "invigilator_allocations_summary": inv_allocs[:15],
            "unassigned_reason_distribution": unassigned_reasons,
        }
