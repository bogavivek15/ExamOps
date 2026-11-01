"""
ExamOps Scheduling Engine — Hard Constraints & Validation Engine
Evaluates candidate assignments against authoritative institutional rules.
"""
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Set, Optional, Tuple, Any
from backend.scheduler.models import (
    ExamModel,
    RoomModel,
    InvigilatorModel,
    ExamParticipant,
    CandidateSlot,
    RoomAllocation,
    ValidationResult,
)

class ConstraintChecker:
    @staticmethod
    def is_timeslot_overlapping(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """Determines if two open-ended intervals [start1, end1) and [start2, end2) overlap."""
        return max(start1, start2) < min(end1, end2)

    @staticmethod
    def check_student_non_overlap(
        participants: List[ExamParticipant],
        slot_start: datetime,
        slot_end: datetime,
        student_calendar: Dict[str, List[Tuple[datetime, datetime, str]]],
    ) -> ValidationResult:
        """
        Constraint: STUDENT_NON_OVERLAP
        Verifies that no student in the candidate cohort is already committed
        to an overlapping examination.
        """
        for p in participants:
            existing_commitments = student_calendar.get(p.student_id, [])
            for c_start, c_end, exam_code in existing_commitments:
                # Student exam ends at slot_start + student_duration
                p_end = slot_start + timedelta(minutes=p.effective_duration_minutes)
                if ConstraintChecker.is_timeslot_overlapping(slot_start, p_end, c_start, c_end):
                    return ValidationResult(
                        is_valid=False,
                        failed_constraints=["STUDENT_NON_OVERLAP"],
                        reason_codes=["STUDENT_CONFLICT"],
                        details={
                            "conflicted_student_id": p.student_id,
                            "conflicted_student_code": p.student_code,
                            "overlapping_exam_code": exam_code,
                            "conflict_window": f"{max(slot_start, c_start)} to {min(p_end, c_end)}",
                        },
                    )
        return ValidationResult(is_valid=True)

    @staticmethod
    def check_room_availability(
        room: RoomModel,
        start_dt: datetime,
        end_dt: datetime,
    ) -> ValidationResult:
        """
        Constraint: ROOM_UNAVAILABLE
        Verifies that the venue is within operating hours and has no scheduled closures.
        """
        exam_date = start_dt.date()
        exam_dow = exam_date.weekday()
        exam_start_t = start_dt.time()
        exam_end_t = end_dt.time()

        # 1. Check for specific closures on this date
        for closure in room.closures:
            c_date = closure.get("specific_date")
            if c_date:
                c_d = date.fromisoformat(c_date) if isinstance(c_date, str) else c_date
                if c_d == exam_date:
                    c_start = time.fromisoformat(closure["start_time"]) if isinstance(closure["start_time"], str) else closure["start_time"]
                    c_end = time.fromisoformat(closure["end_time"]) if isinstance(closure["end_time"], str) else closure["end_time"]
                    if max(exam_start_t, c_start) < min(exam_end_t, c_end):
                        return ValidationResult(
                            is_valid=False,
                            failed_constraints=["ROOM_UNAVAILABLE"],
                            reason_codes=["ROOM_CLOSED_FOR_MAINTENANCE"],
                            details={"room_code": room.room_code, "reason": closure.get("reason", "Closure")},
                        )

        # 2. Check operating window
        is_covered = False
        for op in room.operating_hours:
            if op.get("day_of_week") == exam_dow:
                op_start = time.fromisoformat(op["start_time"]) if isinstance(op["start_time"], str) else op["start_time"]
                op_end = time.fromisoformat(op["end_time"]) if isinstance(op["end_time"], str) else op["end_time"]
                if exam_start_t >= op_start and exam_end_t <= op_end:
                    is_covered = True
                    break

        if not is_covered and room.operating_hours:
            return ValidationResult(
                is_valid=False,
                failed_constraints=["ROOM_UNAVAILABLE"],
                reason_codes=["OUTSIDE_OPERATING_HOURS"],
                details={"room_code": room.room_code},
            )

        return ValidationResult(is_valid=True)

    @staticmethod
    def check_room_equipment(
        room: RoomModel,
        required_equipment_codes: Set[str],
    ) -> ValidationResult:
        """
        Constraint: EQUIPMENT_MISMATCH
        Verifies that the venue possesses all mandatory equipment items.
        """
        missing = required_equipment_codes - room.equipment_codes
        if missing:
            return ValidationResult(
                is_valid=False,
                failed_constraints=["EQUIPMENT_MISMATCH"],
                reason_codes=["REQUIRED_EQUIPMENT_UNAVAILABLE"],
                details={"room_code": room.room_code, "missing_equipment": list(missing)},
            )
        return ValidationResult(is_valid=True)

    @staticmethod
    def check_room_accommodation(
        room: RoomModel,
        seated_students: List[ExamParticipant],
    ) -> ValidationResult:
        """
        Constraint: ACCOMMODATION_BREACH
        Ensures students requiring accessible desks or quiet rooms are in compliant venues.
        """
        for s in seated_students:
            if s.requires_accessible_room and not room.is_accessible:
                return ValidationResult(
                    is_valid=False,
                    failed_constraints=["ACCOMMODATION_BREACH"],
                    reason_codes=["ACCESSIBILITY_MISMATCH"],
                    details={
                        "student_id": s.student_id,
                        "room_code": room.room_code,
                        "required": "WHEELCHAIR_ACCESSIBLE",
                    },
                )
            if s.requires_low_distraction and len(seated_students) > 15:
                return ValidationResult(
                    is_valid=False,
                    failed_constraints=["ACCOMMODATION_BREACH"],
                    reason_codes=["COHORT_TOO_LARGE_FOR_LOW_DISTRACTION"],
                    details={"seated_count": len(seated_students), "max_allowed": 15},
                )
        return ValidationResult(is_valid=True)

    @staticmethod
    def check_invigilator_conflicts(
        invigilator: InvigilatorModel,
        start_dt: datetime,
        end_dt: datetime,
        invigilator_calendar: Dict[str, List[Tuple[datetime, datetime, str]]],
        daily_hours: Dict[Tuple[str, date], float],
        weekly_hours: Dict[Tuple[str, int], float],
    ) -> ValidationResult:
        """
        Constraint: INVIGILATOR_DOUBLE_BOOKED & INVIGILATOR_WORKLOAD_EXCEEDED
        Verifies that the staff member is not double-booked and remains within workload caps.
        """
        # Double-booking check
        existing_shifts = invigilator_calendar.get(invigilator.id, [])
        for s_start, s_end, room_code in existing_shifts:
            if ConstraintChecker.is_timeslot_overlapping(start_dt, end_dt, s_start, s_end):
                return ValidationResult(
                    is_valid=False,
                    failed_constraints=["INVIGILATOR_DOUBLE_BOOKED"],
                    reason_codes=["NO_INVIGILATOR_AVAILABLE"],
                    details={
                        "invigilator_code": invigilator.invigilator_code,
                        "conflicting_room": room_code,
                    },
                )

        # Workload checks
        duration_hours = (end_dt - start_dt).total_seconds() / 3600.0
        shift_date = start_dt.date()
        week_num = shift_date.isocalendar()[1]

        current_daily = daily_hours.get((invigilator.id, shift_date), 0.0)
        if (current_daily + duration_hours) > invigilator.max_hours_per_day:
            return ValidationResult(
                is_valid=False,
                failed_constraints=["INVIGILATOR_WORKLOAD_EXCEEDED"],
                reason_codes=["WORKLOAD_CAP_EXCEEDED"],
                details={
                    "invigilator_code": invigilator.invigilator_code,
                    "attempted_daily_hours": current_daily + duration_hours,
                    "max_daily_hours": invigilator.max_hours_per_day,
                },
            )

        current_weekly = weekly_hours.get((invigilator.id, week_num), 0.0)
        if (current_weekly + duration_hours) > invigilator.max_hours_per_week:
            return ValidationResult(
                is_valid=False,
                failed_constraints=["INVIGILATOR_WORKLOAD_EXCEEDED"],
                reason_codes=["WORKLOAD_CAP_EXCEEDED"],
                details={
                    "invigilator_code": invigilator.invigilator_code,
                    "attempted_weekly_hours": current_weekly + duration_hours,
                    "max_weekly_hours": invigilator.max_hours_per_week,
                },
            )

        return ValidationResult(is_valid=True)
