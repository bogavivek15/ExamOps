"""
ExamOps Scheduling Engine — Independent Schedule Validator
Conducts an isolated, zero-shared-state audit of confirmed schedule assignments against all hard constraints.
"""
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from backend.scheduler.models import (
    ExamModel,
    RoomModel,
    InvigilatorModel,
    ValidationResult,
)
from backend.scheduler.constraints import ConstraintChecker

class ScheduleValidator:
    def __init__(
        self,
        exams: List[ExamModel],
        rooms: List[RoomModel],
        invigilators: List[InvigilatorModel],
    ):
        self.exam_by_id = {e.id: e for e in exams}
        self.room_by_id = {r.id: r for r in rooms}
        self.inv_by_id = {i.id: i for i in invigilators}

    def validate_confirmed_schedule(
        self,
        assignments: List[Dict[str, Any]],
        student_seatings: List[Dict[str, Any]],
        invigilator_staffings: List[Dict[str, Any]],
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validates all confirmed assignments from scratch.
        Returns (is_certified_valid, list_of_violations).
        """
        violations = []

        # 1. Audit Single Room Seating Per Student Per Exam
        # student_id + exam_id must appear at most once across student_seatings
        student_exam_seen: Dict[Tuple[str, str], str] = {}
        for s in student_seatings:
            key = (s["student_id"], s["exam_id"])
            if key in student_exam_seen:
                violations.append({
                    "constraint": "SINGLE_ROOM_SEATING_VIOLATION",
                    "severity": "CRITICAL",
                    "student_id": s["student_id"],
                    "exam_id": s["exam_id"],
                    "description": "Student assigned to multiple rooms for the same examination.",
                })
            else:
                student_exam_seen[key] = s["assignment_id"]

        # 2. Audit Student Non-Overlap
        # Group seated intervals by student
        student_intervals: Dict[str, List[Tuple[datetime, datetime, str]]] = defaultdict(list)
        for s in student_seatings:
            st = s["start_time"]
            et = s["end_time"]
            s_start = datetime.fromisoformat(st) if isinstance(st, str) else st
            s_end = datetime.fromisoformat(et) if isinstance(et, str) else et
            student_intervals[s["student_id"]].append((s_start, s_end, s["exam_id"]))

        for student_id, intervals in student_intervals.items():
            intervals.sort(key=lambda x: x[0])
            for i in range(len(intervals) - 1):
                cur_s, cur_e, e1 = intervals[i]
                nxt_s, nxt_e, e2 = intervals[i + 1]
                if cur_e > nxt_s:
                    violations.append({
                        "constraint": "STUDENT_NON_OVERLAP",
                        "severity": "CRITICAL",
                        "student_id": student_id,
                        "exam_id_1": e1,
                        "exam_id_2": e2,
                        "description": f"Student has overlapping examinations: {cur_s} to {cur_e} and {nxt_s} to {nxt_e}",
                    })

        # 3. Audit Room Capacity & Double Booking
        room_intervals: Dict[str, List[Tuple[datetime, datetime, str, int]]] = defaultdict(list)
        assignment_seated_counts: Dict[str, int] = defaultdict(int)
        for s in student_seatings:
            assignment_seated_counts[s["assignment_id"]] += 1

        for a in assignments:
            st = a["start_time"]
            et = a["end_time"]
            a_start = datetime.fromisoformat(st) if isinstance(st, str) else st
            a_end = datetime.fromisoformat(et) if isinstance(et, str) else et
            r_id = a["room_id"]
            room = self.room_by_id.get(r_id)
            seated = assignment_seated_counts.get(a["id"], 0)

            # Capacity check
            if room and seated > room.exam_capacity:
                violations.append({
                    "constraint": "ROOM_CAPACITY_EXCEEDED",
                    "severity": "CRITICAL",
                    "room_id": r_id,
                    "assignment_id": a["id"],
                    "seated_count": seated,
                    "room_exam_capacity": room.exam_capacity,
                    "description": f"Seated count {seated} exceeds exam capacity {room.exam_capacity}",
                })

            # Check room closures & operating hours
            if room:
                ra_chk = ConstraintChecker.check_room_availability(room, a_start, a_end)
                if not ra_chk.is_valid:
                    violations.append({
                        "constraint": "ROOM_UNAVAILABLE",
                        "severity": "CRITICAL",
                        "room_id": r_id,
                        "assignment_id": a["id"],
                        "details": ra_chk.details,
                        "description": f"Room {room.room_code} scheduled during closure or outside hours",
                    })

            room_intervals[r_id].append((a_start, a_end, a["id"], seated))

        # Check room overlapping assignments
        for r_id, intervals in room_intervals.items():
            intervals.sort(key=lambda x: x[0])
            for i in range(len(intervals) - 1):
                cur_s, cur_e, a1, _ = intervals[i]
                nxt_s, nxt_e, a2, _ = intervals[i + 1]
                if cur_e > nxt_s:
                    violations.append({
                        "constraint": "ROOM_DOUBLE_BOOKED",
                        "severity": "CRITICAL",
                        "room_id": r_id,
                        "assignment_id_1": a1,
                        "assignment_id_2": a2,
                        "description": f"Room allocated to overlapping assignments: {cur_s} to {cur_e} and {nxt_s} to {nxt_e}",
                    })

        # 4. Audit Accommodations
        for s in student_seatings:
            r_id = s.get("room_id")
            room = self.room_by_id.get(r_id)
            if s.get("requires_accessible_room") and room and not room.is_accessible:
                violations.append({
                    "constraint": "ACCOMMODATION_BREACH",
                    "severity": "CRITICAL",
                    "student_id": s["student_id"],
                    "room_id": r_id,
                    "description": "Student requiring wheelchair access placed in non-accessible venue.",
                })

        # 5. Audit Invigilator Double-Booking & Workload
        inv_intervals: Dict[str, List[Tuple[datetime, datetime, str]]] = defaultdict(list)
        inv_daily_hours: Dict[Tuple[str, date], float] = defaultdict(float)
        inv_weekly_hours: Dict[Tuple[str, int], float] = defaultdict(float)

        for staff in invigilator_staffings:
            st = staff["start_time"]
            et = staff["end_time"]
            inv_start = datetime.fromisoformat(st) if isinstance(st, str) else st
            inv_end = datetime.fromisoformat(et) if isinstance(et, str) else et
            inv_id = staff["invigilator_id"]
            inv = self.inv_by_id.get(inv_id)

            dur_hrs = (inv_end - inv_start).total_seconds() / 3600.0
            shift_d = inv_start.date()
            week_num = shift_d.isocalendar()[1]

            inv_daily_hours[(inv_id, shift_d)] += dur_hrs
            inv_weekly_hours[(inv_id, week_num)] += dur_hrs
            inv_intervals[inv_id].append((inv_start, inv_end, staff.get("assignment_id", "")))

            # Check daily/weekly workload caps
            if inv:
                if inv_daily_hours[(inv_id, shift_d)] > (inv.max_hours_per_day + 1e-4):
                    violations.append({
                        "constraint": "INVIGILATOR_WORKLOAD_EXCEEDED",
                        "severity": "CRITICAL",
                        "invigilator_id": inv_id,
                        "date": shift_d.isoformat(),
                        "hours": inv_daily_hours[(inv_id, shift_d)],
                        "cap": inv.max_hours_per_day,
                        "description": "Daily workload cap exceeded.",
                    })
                if inv_weekly_hours[(inv_id, week_num)] > (inv.max_hours_per_week + 1e-4):
                    violations.append({
                        "constraint": "INVIGILATOR_WORKLOAD_EXCEEDED",
                        "severity": "CRITICAL",
                        "invigilator_id": inv_id,
                        "week": week_num,
                        "hours": inv_weekly_hours[(inv_id, week_num)],
                        "cap": inv.max_hours_per_week,
                        "description": "Weekly workload cap exceeded.",
                    })

        # Check invigilator double-booking
        for inv_id, intervals in inv_intervals.items():
            intervals.sort(key=lambda x: x[0])
            for i in range(len(intervals) - 1):
                cur_s, cur_e, a1 = intervals[i]
                nxt_s, nxt_e, a2 = intervals[i + 1]
                if cur_e > nxt_s:
                    violations.append({
                        "constraint": "INVIGILATOR_DOUBLE_BOOKED",
                        "severity": "CRITICAL",
                        "invigilator_id": inv_id,
                        "assignment_1": a1,
                        "assignment_2": a2,
                        "description": f"Invigilator double-booked: {cur_s} to {cur_e} and {nxt_s} to {nxt_e}",
                    })

        is_certified_valid = (len(violations) == 0)
        return is_certified_valid, violations

