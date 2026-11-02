"""
ExamOps Scheduling Engine — Data Models and Telemetry Structures
"""
from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import List, Dict, Set, Optional, Tuple, Any

@dataclass
class ExamParticipant:
    student_id: str
    student_code: str
    first_name: str
    last_name: str
    base_duration_minutes: int
    extra_duration_minutes: int = 0
    effective_duration_minutes: int = 120
    requires_accessible_room: bool = False
    requires_low_distraction: bool = False
    requires_special_equipment: Optional[str] = None
    accommodation_details: Optional[Dict[str, Any]] = None

@dataclass
class ExamRequirementModel:
    id: str
    requirement_code: str
    requirement_type: str  # REQUIRED_EQUIPMENT, ROOM_FEATURE, ROOM_CAPACITY_MIN
    value: str
    is_mandatory: bool = True

@dataclass
class ExamModel:
    id: str
    exam_code: str
    course_id: str
    course_code: str
    title: str
    duration_minutes: int
    priority: int
    requirements: List[ExamRequirementModel] = field(default_factory=list)
    participants: List[ExamParticipant] = field(default_factory=list)

@dataclass
class RoomModel:
    id: str
    room_code: str
    name: str
    building: str
    floor: int
    is_accessible: bool
    standard_capacity: int
    exam_capacity: int
    equipment_codes: Set[str] = field(default_factory=set)
    operating_hours: List[Dict[str, Any]] = field(default_factory=list)
    closures: List[Dict[str, Any]] = field(default_factory=list)
    operating_by_dow: Dict[int, List[Tuple[time, time]]] = field(default_factory=dict, init=False)
    closures_by_date: Dict[date, List[Tuple[time, time, str]]] = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.operating_by_dow = {}
        for op in self.operating_hours:
            dow = op.get("day_of_week")
            if dow is not None:
                st = time.fromisoformat(op["start_time"]) if isinstance(op["start_time"], str) else op["start_time"]
                et = time.fromisoformat(op["end_time"]) if isinstance(op["end_time"], str) else op["end_time"]
                self.operating_by_dow.setdefault(int(dow), []).append((st, et))

        self.closures_by_date = {}
        for c in self.closures:
            c_date = c.get("specific_date")
            if c_date:
                cd = date.fromisoformat(c_date) if isinstance(c_date, str) else c_date
                st = time.fromisoformat(c["start_time"]) if isinstance(c["start_time"], str) else c["start_time"]
                et = time.fromisoformat(c["end_time"]) if isinstance(c["end_time"], str) else c["end_time"]
                reason = c.get("reason", "Closure")
                self.closures_by_date.setdefault(cd, []).append((st, et, reason))

@dataclass
class InvigilatorModel:
    id: str
    invigilator_code: str
    first_name: str
    last_name: str
    department: str
    max_hours_per_day: float = 8.0
    max_hours_per_week: float = 25.0
    availabilities: List[Dict[str, Any]] = field(default_factory=list)
    shifts_by_dow: Dict[int, List[Tuple[time, time]]] = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.shifts_by_dow = {}
        for av in self.availabilities:
            if av.get("availability_type") == "AVAILABLE":
                dow = av.get("day_of_week")
                if dow is not None:
                    st = time.fromisoformat(av["start_time"]) if isinstance(av["start_time"], str) else av["start_time"]
                    et = time.fromisoformat(av["end_time"]) if isinstance(av["end_time"], str) else av["end_time"]
                    self.shifts_by_dow.setdefault(int(dow), []).append((st, et))

@dataclass
class CandidateSlot:
    slot_index: int
    date_val: date
    start_time: time
    end_time: time
    start_dt: datetime
    end_dt: datetime

@dataclass
class RoomAllocation:
    room: RoomModel
    seated_students: List[ExamParticipant]
    room_start_dt: datetime
    room_end_dt: datetime
    effective_duration_minutes: int
    assigned_invigilators: List[InvigilatorModel] = field(default_factory=list)

@dataclass
class CandidateAssignment:
    exam: ExamModel
    slot: CandidateSlot
    allocations: List[RoomAllocation]
    score: Tuple[int, int, float, int]  # (num_rooms, wasted_seats, inv_workload, slot_index)

@dataclass
class ValidationResult:
    is_valid: bool
    failed_constraints: List[str] = field(default_factory=list)
    reason_codes: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionRecord:
    exam_id: str
    exam_code: str
    decision_order: int
    is_assigned: bool
    reason_codes: List[str] = field(default_factory=list)
    selected_candidate: Optional[Dict[str, Any]] = None
    candidate_details: Dict[str, Any] = field(default_factory=dict)

