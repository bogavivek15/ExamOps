"""
ExamOps Scheduling Engine — Candidate Slot Generator
Generates feasible discrete time slots across the institutional examination calendar.
"""
from datetime import date, time, datetime, timedelta, timezone
from typing import List
from backend.scheduler.models import CandidateSlot

class CandidateSlotGenerator:
    def __init__(
        self,
        start_date: date,
        end_date: date,
        daily_start_time: time = time(8, 0),
        daily_end_time: time = time(18, 0),
        slot_granularity_minutes: int = 30,
        skip_sundays: bool = True,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.daily_start_time = daily_start_time
        self.daily_end_time = daily_end_time
        self.slot_granularity = timedelta(minutes=slot_granularity_minutes)
        self.skip_sundays = skip_sundays

    def generate_slots(self, max_duration_minutes: int) -> List[CandidateSlot]:
        """
        Generates candidate time slots where an exam of length max_duration_minutes
        can finish before daily operating closing time.
        """
        slots = []
        slot_index = 0
        current_date = self.start_date
        exam_duration = timedelta(minutes=max_duration_minutes)

        while current_date <= self.end_date:
            # Day of week: Monday=0, Sunday=6
            if self.skip_sundays and current_date.weekday() == 6:
                current_date += timedelta(days=1)
                continue

            day_start_dt = datetime.combine(current_date, self.daily_start_time, tzinfo=timezone.utc)
            day_end_dt = datetime.combine(current_date, self.daily_end_time, tzinfo=timezone.utc)

            current_dt = day_start_dt
            while (current_dt + exam_duration) <= day_end_dt:
                slot_end_dt = current_dt + exam_duration
                slots.append(CandidateSlot(
                    slot_index=slot_index,
                    date_val=current_date,
                    start_time=current_dt.time(),
                    end_time=slot_end_dt.time(),
                    start_dt=current_dt,
                    end_dt=slot_end_dt,
                ))
                slot_index += 1
                current_dt += self.slot_granularity

            current_date += timedelta(days=1)

        return slots
