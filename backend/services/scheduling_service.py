"""
ExamOps Scheduling Run Service
Manages scheduling run lifecycle: Creation -> Execution -> Validation -> Approval -> Publication.
Integrates the deterministic Python scheduling engine with Supabase PostgreSQL.
"""
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, date, time, timezone
import uuid
import json
from psycopg2.extras import execute_values

from backend.database import get_db_connection, get_db_cursor, execute_query, execute_mutation
from backend.scheduler.models import (
    ExamModel,
    RoomModel,
    InvigilatorModel,
    ExamParticipant,
    ExamRequirementModel,
)
from backend.scheduler.engine import SchedulingEngine
from backend.services.analytics_service import invalidate_analytics_cache

class SchedulingService:
    @staticmethod
    def list_runs(academic_period_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if academic_period_id:
            sql = """
            SELECT sr.*, ap.name as academic_period_name, ap.code as period_code,
                   up.display_name as creator_name
            FROM scheduling_runs sr
            JOIN academic_periods ap ON ap.id = sr.academic_period_id
            LEFT JOIN user_profiles up ON up.id = sr.created_by
            WHERE sr.academic_period_id = %s
            ORDER BY sr.created_at DESC
            LIMIT %s OFFSET %s;
            """
            return execute_query(sql, (academic_period_id, limit, offset))
        
        sql = """
        SELECT sr.*, ap.name as academic_period_name, ap.code as period_code,
               up.display_name as creator_name
        FROM scheduling_runs sr
        JOIN academic_periods ap ON ap.id = sr.academic_period_id
        LEFT JOIN user_profiles up ON up.id = sr.created_by
        ORDER BY sr.created_at DESC
        LIMIT %s OFFSET %s;
        """
        return execute_query(sql, (limit, offset))

    @staticmethod
    def get_run_by_id(run_id: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT sr.*, ap.name as academic_period_name, ap.code as period_code,
               up.display_name as creator_name
        FROM scheduling_runs sr
        JOIN academic_periods ap ON ap.id = sr.academic_period_id
        LEFT JOIN user_profiles up ON up.id = sr.created_by
        WHERE sr.id = %s;
        """
        return execute_query(sql, (run_id,), fetch_one=True)

    @staticmethod
    def create_scheduling_run(
        academic_period_id: str,
        created_by: Optional[str] = None,
        algorithm_version: str = "1.0.0",
        seed: int = 20261022,
    ) -> Dict[str, Any]:
        """Creates a new scheduling run record in DRAFT status."""
        import hashlib
        today_digits = datetime.now().strftime('%Y%m%d')
        existing_runs_today = execute_query(
            "SELECT count(*) as c FROM scheduling_runs WHERE run_code LIKE %s;",
            (f"RUN-{today_digits}-%",),
            fetch_one=True,
        )["c"]
        run_seq = f"{existing_runs_today + 1:04d}"
        run_code = f"RUN-{today_digits}-{run_seq}"
        run_id = str(uuid.uuid4())

        # Count total exams for the period
        exam_count = execute_query(
            "SELECT count(*) as cnt FROM exams WHERE academic_period_id = %s;",
            (academic_period_id,),
            fetch_one=True,
        )["cnt"]

        hash_payload = f"{academic_period_id}:{algorithm_version}:{seed}:{run_id}:{exam_count}"
        input_snapshot_hash = hashlib.sha256(hash_payload.encode()).hexdigest()

        # NOTE: Handle unscheduled exams honestly. When a run is newly created in DRAFT,
        # all exams are unassigned. Never report unassigned_count = 0 when exams remain unscheduled!
        sql = """
        INSERT INTO scheduling_runs (
            id, run_code, academic_period_id, created_by, algorithm_version,
            seed, input_snapshot_hash, status, total_exams, scheduled_count, unassigned_count
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'DRAFT', %s, 0, %s)
        RETURNING *;
        """
        with get_db_cursor(commit=True) as cur:
            cur.execute(
                sql,
                (run_id, run_code, academic_period_id, created_by, algorithm_version, seed, input_snapshot_hash, exam_count, exam_count),
            )
            run_record = cur.fetchone()
            invalidate_analytics_cache()
            return dict(run_record) if run_record else {}

    @staticmethod
    def execute_scheduling_run(run_id: str) -> Dict[str, Any]:
        """
        Executes the deterministic scheduling engine for a specific run.
        Takes input snapshot, runs solver, performs validation, and persists results.
        """
        run = SchedulingService.get_run_by_id(run_id)
        if not run:
            raise ValueError(f"Scheduling run {run_id} not found.")

        if run.get("status") == "PUBLISHED":
            raise ValueError(f"Scheduling run '{run_id}' is already PUBLISHED and cannot be re-executed.")

        period_id = run["academic_period_id"]
        period = execute_query("SELECT * FROM academic_periods WHERE id = %s;", (period_id,), fetch_one=True)
        if not period:
            raise ValueError(f"Academic period {period_id} not found.")

        # Update status to SCHEDULING
        execute_mutation(
            "UPDATE scheduling_runs SET status = 'SCHEDULING', started_at = NOW() WHERE id = %s;",
            (run_id,),
        )

        try:
            # 1. Load active exams and requirements
            exam_rows = execute_query(
                "SELECT * FROM exams WHERE academic_period_id = %s ORDER BY exam_code ASC;",
                (period_id,),
            )
            req_rows = execute_query(
                "SELECT * FROM exam_requirements WHERE exam_id IN (SELECT id FROM exams WHERE academic_period_id = %s);",
                (period_id,),
            )
            reqs_by_exam: Dict[str, List[ExamRequirementModel]] = {}
            for r in req_rows:
                reqs_by_exam.setdefault(str(r["exam_id"]), []).append(
                    ExamRequirementModel(
                        id=str(r["id"]),
                        requirement_code=r["requirement_code"],
                        requirement_type=r["requirement_type"],
                        value=r["value"],
                        is_mandatory=r["is_mandatory"],
                    )
                )

            # 2. Check or create run_exam_students snapshot
            snapshot_rows = execute_query(
                "SELECT * FROM run_exam_students WHERE scheduling_run_id = %s;",
                (run_id,),
            )
            res_map: Dict[Tuple[str, str], str] = {}  # (exam_id, student_id) -> run_exam_student_id
            participants_by_exam: Dict[str, List[ExamParticipant]] = {}

            if not snapshot_rows:
                # Build snapshot from enrollments and accommodations in a single pass
                enrollments = execute_query(
                    """
                    SELECT enr.student_id, enr.course_id, ex.id as exam_id, ex.duration_minutes,
                           s.student_code, s.first_name, s.last_name
                    FROM enrollments enr
                    JOIN exams ex ON ex.course_id = enr.course_id AND ex.academic_period_id = enr.academic_period_id
                    JOIN students s ON s.id = enr.student_id
                    WHERE enr.academic_period_id = %s AND enr.status = 'ACTIVE';
                    """,
                    (period_id,),
                )
                accommodations = execute_query(
                    """
                    SELECT * FROM accommodations 
                    WHERE is_active = TRUE AND CURRENT_DATE BETWEEN effective_start AND effective_end;
                    """
                )
                accs_by_student: Dict[str, List[Dict[str, Any]]] = {}
                for acc in accommodations:
                    accs_by_student.setdefault(str(acc["student_id"]), []).append(acc)

                snapshot_tuples = []
                for row in enrollments:
                    s_id = str(row["student_id"])
                    e_id = str(row["exam_id"])
                    base_dur = row["duration_minutes"]
                    extra_min = 0
                    accessible = False
                    low_dist = False
                    special_eq = None

                    for a in accs_by_student.get(s_id, []):
                        if a.get("extra_time_minutes"):
                            extra_min = max(extra_min, a["extra_time_minutes"])
                        if a.get("accommodation_type") == "ACCESSIBLE_ROOM":
                            accessible = True
                        if a.get("accommodation_type") == "LOW_DISTRACTION":
                            low_dist = True
                        if a.get("required_equipment"):
                            special_eq = a["required_equipment"]

                    eff_dur = base_dur + extra_min
                    has_acc = extra_min > 0 or accessible or low_dist or (special_eq is not None)
                    acc_dict = {"extra_min": extra_min, "accessible": accessible, "low_dist": low_dist} if has_acc else {}

                    res_id = str(uuid.uuid4())
                    res_map[(e_id, s_id)] = res_id

                    snapshot_tuples.append((
                        res_id,
                        run_id,
                        e_id,
                        s_id,
                        base_dur,
                        extra_min,
                        eff_dur,
                        has_acc,
                        json.dumps(acc_dict) if has_acc else None,
                    ))

                    participants_by_exam.setdefault(e_id, []).append(
                        ExamParticipant(
                            student_id=s_id,
                            student_code=row.get("student_code", f"STU-{s_id[:6]}"),
                            first_name=row.get("first_name", "Student"),
                            last_name=row.get("last_name", ""),
                            base_duration_minutes=base_dur,
                            extra_duration_minutes=extra_min,
                            effective_duration_minutes=eff_dur,
                            requires_accessible_room=accessible,
                            requires_low_distraction=low_dist,
                            accommodation_details=acc_dict,
                        )
                    )

                if snapshot_tuples:
                    with get_db_cursor(commit=True) as cur:
                        execute_values(
                            cur,
                            """
                            INSERT INTO run_exam_students (
                                id, scheduling_run_id, exam_id, student_id,
                                base_duration_minutes, extra_duration_minutes, effective_duration_minutes,
                                has_accommodation, accommodation_details
                            ) VALUES %s
                            ON CONFLICT (scheduling_run_id, exam_id, student_id) DO NOTHING;
                            """,
                            snapshot_tuples,
                            page_size=2000,
                        )
            else:
                student_meta = {
                    str(s["id"]): s
                    for s in execute_query("SELECT id, student_code, first_name, last_name FROM students;")
                }
                for snap in snapshot_rows:
                    e_id = str(snap["exam_id"])
                    s_id = str(snap["student_id"])
                    res_map[(e_id, s_id)] = str(snap["id"])
                    sm = student_meta.get(s_id, {})
                    acc_details = snap.get("accommodation_details") or {}
                    participants_by_exam.setdefault(e_id, []).append(
                        ExamParticipant(
                            student_id=s_id,
                            student_code=sm.get("student_code", f"STU-{s_id[:6]}"),
                            first_name=sm.get("first_name", "Student"),
                            last_name=sm.get("last_name", ""),
                            base_duration_minutes=snap["base_duration_minutes"],
                            extra_duration_minutes=snap["extra_duration_minutes"],
                            effective_duration_minutes=snap["effective_duration_minutes"],
                            requires_accessible_room=acc_details.get("accessible", False),
                            requires_low_distraction=acc_details.get("low_dist", False),
                            accommodation_details=acc_details,
                        )
                    )

            # Build ExamModel instances
            exam_models = []
            for ex in exam_rows:
                e_id = str(ex["id"])
                exam_models.append(
                    ExamModel(
                        id=e_id,
                        exam_code=ex["exam_code"],
                        course_id=str(ex["course_id"]),
                        course_code=ex.get("course_code", ex["exam_code"][:7]),
                        title=ex["title"],
                        duration_minutes=ex["duration_minutes"],
                        priority=ex.get("priority", 3),
                        requirements=reqs_by_exam.get(e_id, []),
                        participants=participants_by_exam.get(e_id, []),
                    )
                )

            # 3. Load Rooms
            room_rows = execute_query("SELECT * FROM rooms WHERE status = 'AVAILABLE';")
            caps_rows = execute_query(
                "SELECT * FROM room_capacities WHERE CURRENT_DATE BETWEEN effective_start AND effective_end;"
            )
            caps_by_room = {str(c["room_id"]): c for c in caps_rows}
            eq_rows = execute_query(
                """
                SELECT re.room_id, et.code as type_code 
                FROM room_equipment re
                JOIN equipment_types et ON et.id = re.equipment_type_id;
                """
            )
            eq_by_room: Dict[str, Set[str]] = {}
            for eq in eq_rows:
                eq_by_room.setdefault(str(eq["room_id"]), set()).add(eq["type_code"])

            ra_rows = execute_query("SELECT * FROM room_availabilities;")
            op_by_room: Dict[str, List[Dict[str, Any]]] = {}
            closures_by_room: Dict[str, List[Dict[str, Any]]] = {}
            for ra in ra_rows:
                rid = str(ra["room_id"])
                if ra.get("availability_type") == "AVAILABLE":
                    op_by_room.setdefault(rid, []).append(ra)
                else:
                    closures_by_room.setdefault(rid, []).append(ra)

            room_models = []
            for rm in room_rows:
                r_id = str(rm["id"])
                cap = caps_by_room.get(r_id, {})
                room_models.append(
                    RoomModel(
                        id=r_id,
                        room_code=rm["room_code"],
                        name=rm["name"],
                        building=rm["building"],
                        floor=rm["floor"],
                        is_accessible=rm["is_accessible"],
                        standard_capacity=cap.get("standard_capacity", 50),
                        exam_capacity=cap.get("exam_capacity", 35),
                        equipment_codes=eq_by_room.get(r_id, set()),
                        operating_hours=op_by_room.get(r_id, []),
                        closures=closures_by_room.get(r_id, []),
                    )
                )

            # 4. Load Invigilators
            inv_rows = execute_query("SELECT * FROM invigilators WHERE status = 'ACTIVE';")
            avail_rows = execute_query("SELECT * FROM availabilities;")
            avail_by_inv: Dict[str, List[Dict[str, Any]]] = {}
            for av in avail_rows:
                avail_by_inv.setdefault(str(av["invigilator_id"]), []).append(av)

            inv_models = [
                InvigilatorModel(
                    id=str(i["id"]),
                    invigilator_code=i["invigilator_code"],
                    first_name=i["first_name"],
                    last_name=i["last_name"],
                    department=i["department"],
                    max_hours_per_day=float(i["max_hours_per_day"]),
                    max_hours_per_week=float(i["max_hours_per_week"]),
                    availabilities=avail_by_inv.get(str(i["id"]), []),
                )
                for i in inv_rows
            ]

            # 5. Initialize SchedulingEngine and Solve
            start_date = period.get("exam_start_date") or period["start_date"]
            end_date = period.get("exam_end_date") or period["end_date"]

            engine = SchedulingEngine(
                exams=exam_models,
                rooms=room_models,
                invigilators=inv_models,
                start_date=start_date,
                end_date=end_date,
            )
            solver_output = engine.execute_schedule()

            # 6. Persist results in atomic transaction
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Clean up any prior execution artifacts for this run
                    cur.execute("DELETE FROM assignment_students WHERE scheduling_run_id = %s;", (run_id,))
                    cur.execute("DELETE FROM assignment_invigilators WHERE assignment_id IN (SELECT id FROM schedule_assignments WHERE scheduling_run_id = %s);", (run_id,))
                    cur.execute("DELETE FROM schedule_assignments WHERE scheduling_run_id = %s;", (run_id,))
                    cur.execute("DELETE FROM scheduling_decisions WHERE scheduling_run_id = %s;", (run_id,))
                    cur.execute("DELETE FROM validation_issues WHERE scheduling_run_id = %s;", (run_id,))

                    # Batch Insert ScheduleAssignments
                    asgn_tuples = []
                    assignment_id_map: Dict[Tuple[str, str], str] = {} # (exam_id, room_id) -> db_assignment_id
                    for asgn in solver_output["assignments"]:
                        db_asgn_id = str(uuid.uuid4())
                        assignment_id_map[(asgn["exam_id"], asgn["room_id"])] = db_asgn_id
                        asgn_tuples.append((
                            db_asgn_id,
                            asgn["assignment_code"],
                            run_id,
                            asgn["exam_id"],
                            asgn["room_id"],
                            asgn["start_time"],
                            asgn["end_time"],
                            "CONFIRMED",
                        ))
                    if asgn_tuples:
                        execute_values(
                            cur,
                            """
                            INSERT INTO schedule_assignments (
                                id, assignment_code, scheduling_run_id, exam_id, room_id,
                                start_time, end_time, status
                            ) VALUES %s;
                            """,
                            asgn_tuples,
                            page_size=1000,
                        )

                    # Batch Insert AssignmentStudents
                    seat_tuples = []
                    for seat in solver_output["student_seatings"]:
                        db_asgn_id = assignment_id_map.get((seat["exam_id"], seat["room_id"]))
                        res_id = res_map.get((seat["exam_id"], seat["student_id"]))
                        if db_asgn_id and res_id:
                            seat_tuples.append((
                                str(uuid.uuid4()),
                                db_asgn_id,
                                res_id,
                                run_id,
                                seat["exam_id"],
                                seat["student_id"],
                                seat["room_id"],
                                seat["effective_duration_minutes"],
                            ))
                    if seat_tuples:
                        execute_values(
                            cur,
                            """
                            INSERT INTO assignment_students (
                                id, assignment_id, run_exam_student_id, scheduling_run_id,
                                exam_id, student_id, room_id, effective_duration_minutes
                            ) VALUES %s
                            ON CONFLICT (assignment_id, student_id) DO NOTHING;
                            """,
                            seat_tuples,
                            page_size=2000,
                        )

                    # Batch Insert AssignmentInvigilators
                    inv_tuples = []
                    asgn_lookup = {a["id"]: (a["exam_id"], a["room_id"]) for a in solver_output["assignments"]}
                    for inv in solver_output["invigilator_staffings"]:
                        key = asgn_lookup.get(inv["assignment_id"])
                        if key:
                            target_db_asgn_id = assignment_id_map.get(key)
                            if target_db_asgn_id:
                                inv_tuples.append((
                                    str(uuid.uuid4()),
                                    target_db_asgn_id,
                                    inv["invigilator_id"],
                                    "PRIMARY",
                                ))
                    if inv_tuples:
                        execute_values(
                            cur,
                            """
                            INSERT INTO assignment_invigilators (
                                id, assignment_id, invigilator_id, role
                            ) VALUES %s
                            ON CONFLICT (assignment_id, invigilator_id) DO NOTHING;
                            """,
                            inv_tuples,
                            page_size=1000,
                        )

                    # Batch Insert SchedulingDecisions (deduplicated by exam_id to keep latest outcome)
                    latest_decisions = {}
                    for dec in solver_output["decisions"]:
                        latest_decisions[dec["exam_id"]] = dec

                    dec_tuples = [
                        (
                            str(uuid.uuid4()),
                            run_id,
                            dec["exam_id"],
                            dec["decision_order"],
                            dec["is_assigned"],
                            dec["reason_codes"],
                            json.dumps(dec.get("selected_candidate")) if dec.get("selected_candidate") else None,
                            json.dumps(dec.get("candidate_details")) if dec.get("candidate_details") else None,
                        )
                        for dec in latest_decisions.values()
                    ]
                    if dec_tuples:
                        execute_values(
                            cur,
                            """
                            INSERT INTO scheduling_decisions (
                                id, scheduling_run_id, exam_id, decision_order,
                                is_assigned, reason_codes, selected_candidate, candidate_details
                            ) VALUES %s
                            ON CONFLICT (scheduling_run_id, exam_id) DO UPDATE SET
                                is_assigned = EXCLUDED.is_assigned,
                                reason_codes = EXCLUDED.reason_codes,
                                selected_candidate = EXCLUDED.selected_candidate,
                                candidate_details = EXCLUDED.candidate_details,
                                decision_order = EXCLUDED.decision_order;
                            """,
                            dec_tuples,
                            page_size=1000,
                        )

                    # Insert Validation Issues if any
                    for vi in solver_output["violations"]:
                        cur.execute(
                            """
                            INSERT INTO validation_issues (
                                id, scheduling_run_id, issue_type, severity, description, resolution_status
                            ) VALUES (%s, %s, %s, 'ERROR', %s, 'OPEN');
                            """,
                            (
                                str(uuid.uuid4()),
                                run_id,
                                "HARD_CONSTRAINT_VIOLATION",
                                str(vi),
                            )
                        )

                    # Update SchedulingRun final metrics
                    final_status = "REVIEW_REQUIRED"
                    cur.execute(
                        """
                        UPDATE scheduling_runs
                        SET status = %s,
                            total_exams = %s,
                            scheduled_count = %s,
                            unassigned_count = %s,
                            completed_at = NOW()
                        WHERE id = %s;
                        """,
                        (
                            final_status,
                            solver_output["metrics"]["total_exams"],
                            solver_output["metrics"]["scheduled_count"],
                            solver_output["metrics"]["unassigned_count"],
                            run_id,
                        )
                    )
                conn.commit()

            invalidate_analytics_cache()

            return {
                "success": True,
                "run_id": run_id,
                "status": final_status,
                "metrics": solver_output["metrics"],
                "violations_count": solver_output["violations_count"],
            }

        except Exception as e:
            execute_mutation(
                "UPDATE scheduling_runs SET status = 'CANCELLED', completed_at = NOW() WHERE id = %s;",
                (run_id,),
            )
            raise e

    @staticmethod
    def get_run_assignments(
        run_id: str,
        exam_id: Optional[str] = None,
        room_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        conditions = ["sa.scheduling_run_id = %s"]
        params: List[Any] = [run_id]

        if exam_id:
            conditions.append("sa.exam_id = %s")
            params.append(exam_id)
        if room_id:
            conditions.append("sa.room_id = %s")
            params.append(room_id)

        sql = f"""
        SELECT sa.*,
               ex.exam_code, ex.title as exam_title,
               r.room_code, r.name as room_name, r.building,
               (SELECT count(*) FROM assignment_students ast WHERE ast.assignment_id = sa.id) as seated_student_count
        FROM schedule_assignments sa
        JOIN exams ex ON ex.id = sa.exam_id
        JOIN rooms r ON r.id = sa.room_id
        WHERE {' AND '.join(conditions)}
        ORDER BY sa.start_time ASC, ex.exam_code ASC
        LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return execute_query(sql, tuple(params))

    @staticmethod
    def get_run_decisions(
        run_id: str,
        exam_id: Optional[str] = None,
        is_assigned: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        conditions = ["sd.scheduling_run_id = %s"]
        params: List[Any] = [run_id]

        if exam_id:
            conditions.append("sd.exam_id = %s")
            params.append(exam_id)
        if is_assigned is not None:
            conditions.append("sd.is_assigned = %s")
            params.append(is_assigned)

        sql = f"""
        SELECT sd.*, ex.exam_code, ex.title as exam_title
        FROM scheduling_decisions sd
        JOIN exams ex ON ex.id = sd.exam_id
        WHERE {' AND '.join(conditions)}
        ORDER BY sd.decision_order ASC
        LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return execute_query(sql, tuple(params))

    @staticmethod
    def get_run_validation_issues(run_id: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM validation_issues WHERE scheduling_run_id = %s ORDER BY created_at ASC;"
        return execute_query(sql, (run_id,))

    @staticmethod
    def approve_run(run_id: str, user_id: str) -> Dict[str, Any]:
        """Marks a COMPLETED run as APPROVED after validating that no BLOCKER issues exist."""
        run = SchedulingService.get_run_by_id(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found.")

        if run["status"] not in ("COMPLETED", "REVIEW_REQUIRED"):
            raise ValueError(f"Run status is '{run['status']}', expected 'COMPLETED' or 'REVIEW_REQUIRED'.")

        # Verify no unresolved blocker issues
        blockers = execute_query(
            "SELECT count(*) as cnt FROM validation_issues WHERE scheduling_run_id = %s AND severity = 'BLOCKER' AND resolution_status = 'OPEN';",
            (run_id,),
            fetch_one=True,
        )["cnt"]
        if blockers > 0:
            raise ValueError(f"Cannot approve schedule: {blockers} unresolved blocker issues exist.")

        execute_mutation(
            "UPDATE scheduling_runs SET status = 'APPROVED', updated_at = NOW() WHERE id = %s;",
            (run_id,),
        )
        invalidate_analytics_cache()
        return {"success": True, "run_id": run_id, "status": "APPROVED"}

    @staticmethod
    def publish_run(run_id: str, user_id: str) -> Dict[str, Any]:
        """
        Invokes atomic database publication stored procedure:
        - Locks academic period row
        - Supersedes any currently published run for that period
        - Sets target run to PUBLISHED
        - Marks exams as PUBLISHED
        - Writes schedule_events and audit_logs
        """
        sql = "SELECT publish_schedule_run(%s::uuid, %s::uuid) as result;"
        with get_db_cursor(commit=True) as cur:
            cur.execute(sql, (run_id, user_id))
            res = cur.fetchone()
            invalidate_analytics_cache()
            return res["result"] if res else {"success": False}
