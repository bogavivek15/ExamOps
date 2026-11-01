"""
ExamOps Scheduling Engine — Candidate Scoring Engine
Computes multi-objective lexicographic penalty score for candidate assignments.
"""
from typing import List, Tuple
from backend.scheduler.models import CandidateAssignment, RoomAllocation

def compute_candidate_score(
    allocations: List[RoomAllocation],
    slot_index: int,
) -> Tuple[int, int, float, int]:
    """
    Computes a deterministic lexicographical score (lower is better):
    1. Number of venues allocated (minimize room fragmentation; 1 room preferred).
    2. Wasted seats: sum(room.exam_capacity - seated_count) across all allocated rooms.
    3. Invigilator staffing count.
    4. Slot index (prefers earlier placements in exam calendar).
    """
    num_rooms = len(allocations)
    wasted_seats = sum(a.room.exam_capacity - len(a.seated_students) for a in allocations)
    total_invigilators = sum(len(a.assigned_invigilators) for a in allocations)

    return (num_rooms, wasted_seats, float(total_invigilators), slot_index)
