"""
ExamOps Scheduling Engine — Room Allocator & Multi-Room Splitting
Implements the Seven Room-Splitting Invariants and best-fit venue allocation.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Tuple
from backend.scheduler.models import (
    ExamModel,
    RoomModel,
    ExamParticipant,
    CandidateSlot,
    RoomAllocation,
    ValidationResult,
)
from backend.scheduler.constraints import ConstraintChecker

class RoomAllocator:
    def __init__(self, rooms: List[RoomModel]):
        self.rooms = rooms

    def allocate_rooms(
        self,
        exam: ExamModel,
        slot: CandidateSlot,
        room_calendar: Dict[str, List[Tuple[datetime, datetime, str]]],
    ) -> Tuple[Optional[List[RoomAllocation]], List[str]]:
        """
        Attempts to find a valid room or combination of rooms to seat all participants of the exam.
        Respects the Seven Room-Splitting Invariants:
        1. Primary room selection: Largest suitable venue evaluated first.
        2. Sub-cohort preservation: Students with accommodations placed in compliant rooms.
        3. Minimum venue count: Greedy Best-Fit Decreasing on exam capacity.
        4. Room capacity limit: seated <= room.exam_capacity.
        5. Longest student determines room occupation: max duration of students in that room.
        6. Single room per student: exactly one room per student.
        7. Empty room prohibition: every allocated room has at least 1 student.
        """
        required_eq = {req.value for req in exam.requirements if req.requirement_type == "REQUIRED_EQUIPMENT" and req.is_mandatory}
        total_students = len(exam.participants)
        if total_students == 0:
            return [], []

        # Find all available rooms in this candidate slot
        candidate_rooms = []
        for r in self.rooms:
            # Check mandatory equipment
            eq_res = ConstraintChecker.check_room_equipment(r, required_eq)
            if not eq_res.is_valid:
                continue

            # Check existing room bookings (fast date-bucketed lookup)
            existing_bookings = room_calendar.get((r.id, slot.date_val))
            if existing_bookings is None:
                existing_bookings = room_calendar.get(r.id, [])

            is_booked = False
            for b_start, b_end, b_exam in existing_bookings:
                if max(slot.start_dt, b_start) < min(slot.end_dt, b_end):
                    is_booked = True
                    break
            if is_booked:
                continue

            # Check room availability operating hours & closures
            ra_res = ConstraintChecker.check_room_availability(r, slot.start_dt, slot.end_dt)
            if not ra_res.is_valid:
                continue

            candidate_rooms.append(r)

        if not candidate_rooms:
            return None, ["NO_ROOMS_AVAILABLE"]

        # Sort candidate rooms by exam_capacity descending (Best-Fit Decreasing)
        candidate_rooms.sort(key=lambda r: -r.exam_capacity)

        # Total available capacity check
        total_capacity = sum(r.exam_capacity for r in candidate_rooms)
        if total_capacity < total_students:
            return None, ["CAPACITY_DEFICIT"]

        # Partition students by accommodation requirements (Invariant 2: Sub-cohort preservation)
        accessible_students = [p for p in exam.participants if p.requires_accessible_room]
        low_distraction_students = [p for p in exam.participants if p.requires_low_distraction and not p.requires_accessible_room]
        standard_students = [p for p in exam.participants if not p.requires_accessible_room and not p.requires_low_distraction]

        allocations: List[RoomAllocation] = []
        used_room_ids = set()

        # Helper to seat a student cohort into rooms
        def seat_cohort(cohort: List[ExamParticipant], require_accessible: bool = False, max_cohort_size: Optional[int] = None) -> bool:
            nonlocal candidate_rooms, used_room_ids, allocations
            remaining = list(cohort)
            while remaining:
                # Find best room for this cohort
                eligible_rooms = [
                    r for r in candidate_rooms
                    if r.id not in used_room_ids
                    and (not require_accessible or r.is_accessible)
                ]
                if not eligible_rooms:
                    return False

                # Prefer room closest in capacity to remaining cohort to minimize wasted seats
                # but large enough if possible
                chosen_room = None
                for r in eligible_rooms:
                    if r.exam_capacity >= len(remaining):
                        chosen_room = r # Because sorted descending, keep searching for smallest that fits
                    else:
                        break
                if not chosen_room:
                    chosen_room = eligible_rooms[0] # Take largest available

                cap = chosen_room.exam_capacity
                if max_cohort_size:
                    cap = min(cap, max_cohort_size)

                seated_slice = remaining[:cap]
                remaining = remaining[cap:]
                used_room_ids.add(chosen_room.id)

                # Invariant 5: Longest student determines room end time
                max_student_dur = max(p.effective_duration_minutes for p in seated_slice)
                room_end_dt = slot.start_dt + timedelta(minutes=max_student_dur)

                allocations.append(RoomAllocation(
                    room=chosen_room,
                    seated_students=seated_slice,
                    room_start_dt=slot.start_dt,
                    room_end_dt=room_end_dt,
                    effective_duration_minutes=max_student_dur,
                ))
            return True

        # 1. Seat accessible students first in accessible rooms
        if accessible_students:
            if not seat_cohort(accessible_students, require_accessible=True):
                return None, ["ACCESSIBILITY_MISMATCH"]

        # 2. Seat low-distraction students in rooms with cohort <= 15
        if low_distraction_students:
            if not seat_cohort(low_distraction_students, max_cohort_size=15):
                return None, ["COHORT_TOO_LARGE_FOR_LOW_DISTRACTION"]

        # 3. Seat standard students
        if standard_students:
            # Check if standard students can share space in previously opened rooms that still have capacity
            remaining_standard = list(standard_students)
            for alloc in allocations:
                room_cap = alloc.room.exam_capacity
                if alloc.seated_students and alloc.seated_students[0].requires_low_distraction:
                    continue # Do not mix standard students into low-distraction rooms
                free_space = room_cap - len(alloc.seated_students)
                if free_space > 0 and remaining_standard:
                    slice_to_add = remaining_standard[:free_space]
                    remaining_standard = remaining_standard[free_space:]
                    alloc.seated_students.extend(slice_to_add)
                    # Recalculate room end time
                    max_dur = max(p.effective_duration_minutes for p in alloc.seated_students)
                    alloc.room_end_dt = slot.start_dt + timedelta(minutes=max_dur)
                    alloc.effective_duration_minutes = max_dur

            if remaining_standard:
                if not seat_cohort(remaining_standard):
                    return None, ["CAPACITY_DEFICIT"]

        # Invariant 7: Empty room prohibition
        allocations = [a for a in allocations if len(a.seated_students) > 0]
        if not allocations:
            return None, ["CAPACITY_DEFICIT"]

        return allocations, []

