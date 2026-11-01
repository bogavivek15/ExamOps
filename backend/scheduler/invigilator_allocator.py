"""
ExamOps Scheduling Engine — Invigilator Allocator
Allocates exam invigilators to rooms respecting staffing ratios, availability, and workload limits.
"""
import math
from datetime import datetime, date, time
from typing import List, Dict, Set, Optional, Tuple
from backend.scheduler.models import (
    InvigilatorModel,
    RoomAllocation,
    ValidationResult,
)
from backend.scheduler.constraints import ConstraintChecker

class InvigilatorAllocator:
    def __init__(self, invigilators: List[InvigilatorModel]):
        self.invigilators = invigilators

    def allocate_invigilators(
        self,
        allocations: List[RoomAllocation],
        invigilator_calendar: Dict[str, List[Tuple[datetime, datetime, str]]],
        daily_hours: Dict[Tuple[str, date], float],
        weekly_hours: Dict[Tuple[str, int], float],
    ) -> Tuple[bool, List[str]]:
        """
        Assigns qualified invigilators to each allocated room.
        Staffing ratio: ceil(num_students / 30), minimum 1.
        Returns (success_bool, reason_codes).
        """
        # Track invigilators assigned within this current candidate assignment evaluation
        temporarily_assigned_ids: Set[str] = set()

        for alloc in allocations:
            student_count = len(alloc.seated_students)
            required_count = max(1, math.ceil(student_count / 30.0))

            room_start = alloc.room_start_dt
            room_end = alloc.room_end_dt
            room_code = alloc.room.room_code
            exam_date = room_start.date()
            exam_dow = exam_date.weekday()
            exam_start_t = room_start.time()
            exam_end_t = room_end.time()
            week_num = exam_date.isocalendar()[1]

            # Candidate invigilators who are eligible
            eligible_candidates = []
            for inv in self.invigilators:
                if inv.id in temporarily_assigned_ids:
                    continue

                # 1. Check availability shift window on this date
                is_available = False
                for av in inv.availabilities:
                    if av.get("day_of_week") == exam_dow and av.get("availability_type") == "AVAILABLE":
                        av_start = time.fromisoformat(av["start_time"]) if isinstance(av["start_time"], str) else av["start_time"]
                        av_end = time.fromisoformat(av["end_time"]) if isinstance(av["end_time"], str) else av["end_time"]
                        if exam_start_t >= av_start and exam_end_t <= av_end:
                            is_available = True
                            break
                if not is_available:
                    continue

                # 2. Check conflicts and workload limits
                chk = ConstraintChecker.check_invigilator_conflicts(
                    inv, room_start, room_end, invigilator_calendar, daily_hours, weekly_hours
                )
                if not chk.is_valid:
                    continue

                # Workload sorting key: lowest current weekly hours first (equitable distribution)
                cur_weekly = weekly_hours.get((inv.id, week_num), 0.0)
                cur_daily = daily_hours.get((inv.id, exam_date), 0.0)
                eligible_candidates.append((cur_weekly, cur_daily, inv))

            if len(eligible_candidates) < required_count:
                return False, ["NO_INVIGILATOR_AVAILABLE"]

            # Sort by workload ascending
            eligible_candidates.sort(key=lambda item: (item[0], item[1], item[2].invigilator_code))

            selected = [item[2] for item in eligible_candidates[:required_count]]
            alloc.assigned_invigilators = selected
            for s in selected:
                temporarily_assigned_ids.add(s.id)

        return True, []
