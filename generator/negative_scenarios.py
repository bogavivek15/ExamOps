"""
ExamOps Negative Scenarios & Ground Truth Engine
Generates explicit synthetic test fixtures for the 5 mandatory negative scenarios.
These fixtures are kept strictly isolated from operational scheduler inputs.
"""
from typing import List, Dict, Any

def generate_ground_truth_fixtures(
    students: List[Dict[str, Any]],
    exams: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    invigilators: List[Dict[str, Any]],
    accommodations: List[Dict[str, Any]],
    room_availabilities: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Constructs labelled negative scenario records for verification.
    Each scenario defines:
    - scenario_id
    - scenario_name
    - target_entities
    - injected_anomaly
    - expected_constraint_violated
    - expected_reason_code
    - expected_outcome
    """
    fixtures = []

    # Scenario 1: Student Overlapping Exams
    # Target: First student with multiple enrollments
    s1_student = students[0]
    fixtures.append({
        "scenario_id": "NEG-001",
        "scenario_name": "Student Overlapping Exams",
        "description": "Student is placed in two concurrent examinations simultaneously.",
        "target_student_code": s1_student["student_code"],
        "target_student_id": s1_student["id"],
        "target_exam_codes": [exams[0]["exam_code"], exams[1]["exam_code"]],
        "injected_anomaly": "Simultaneous assignment of both exams at 2026-12-02 09:00:00+00",
        "expected_constraint_violated": "STUDENT_NON_OVERLAP",
        "expected_reason_code": "STUDENT_CONFLICT",
        "expected_outcome": "REJECTED_OR_FLAGGED_AS_CRITICAL",
    })

    # Scenario 2: Room Capacity Exceeded
    # Target: Exam with high enrollment placed in a room smaller than student count
    small_room = min(rooms, key=lambda r: r.get("exam_capacity", 999))
    large_exam = max(exams, key=lambda e: e.get("enrolled_student_count", 0))
    fixtures.append({
        "scenario_id": "NEG-002",
        "scenario_name": "Room Capacity Exceeded",
        "description": "Examination cohort assigned to a room whose exam capacity is lower than student count.",
        "target_room_code": small_room["room_code"],
        "target_room_id": small_room["id"],
        "room_capacity": small_room.get("exam_capacity", 20),
        "target_exam_code": large_exam["exam_code"],
        "target_exam_id": large_exam["id"],
        "exam_student_count": large_exam.get("enrolled_student_count", 50),
        "injected_anomaly": f"Seating {large_exam.get('enrolled_student_count', 50)} students in room with capacity {small_room.get('exam_capacity', 20)}",
        "expected_constraint_violated": "ROOM_CAPACITY_EXCEEDED",
        "expected_reason_code": "CAPACITY_DEFICIT",
        "expected_outcome": "REJECTED_OR_FLAGGED_AS_CRITICAL",
    })

    # Scenario 3: Invigilator Double-Booked
    # Target: Invigilator assigned to two distinct rooms at overlapping times
    target_inv = invigilators[0]
    fixtures.append({
        "scenario_id": "NEG-003",
        "scenario_name": "Invigilator Double-Booked",
        "description": "Same invigilator assigned to supervise two concurrent exams in different rooms.",
        "target_invigilator_code": target_inv["invigilator_code"],
        "target_invigilator_id": target_inv["id"],
        "target_room_codes": [rooms[0]["room_code"], rooms[1]["room_code"]],
        "injected_anomaly": "Simultaneous staffing of INV-000001 to Room 101 and Room 102 at 09:00-11:00",
        "expected_constraint_violated": "INVIGILATOR_DOUBLE_BOOKED",
        "expected_reason_code": "NO_INVIGILATOR_AVAILABLE",
        "expected_outcome": "REJECTED_OR_FLAGGED_AS_CRITICAL",
    })

    # Scenario 4: Accommodation Ignored
    # Target: Student requiring wheelchair accessibility assigned to non-accessible room, or extended time truncated
    wheelchair_acc = next((a for a in accommodations if a["accommodation_type"] == "ACCESSIBLE_ROOM"), None)
    if not wheelchair_acc:
        wheelchair_acc = accommodations[0]
    non_accessible_room = next((r for r in rooms if not r.get("is_accessible", False)), rooms[-1])
    fixtures.append({
        "scenario_id": "NEG-004",
        "scenario_name": "Accommodation Ignored",
        "description": "Student with accessibility requirement seated in non-compliant venue or extended time ignored.",
        "target_student_id": wheelchair_acc["student_id"],
        "accommodation_type": wheelchair_acc["accommodation_type"],
        "target_room_code": non_accessible_room["room_code"],
        "room_is_accessible": non_accessible_room.get("is_accessible", False),
        "injected_anomaly": "Seating student requiring accessible desk in non-accessible venue",
        "expected_constraint_violated": "ACCOMMODATION_BREACH",
        "expected_reason_code": "ACCESSIBILITY_MISMATCH",
        "expected_outcome": "REJECTED_OR_FLAGGED_AS_CRITICAL",
    })

    # Scenario 5: Exam Outside Room Availability
    # Target: Room scheduled during a maintenance closure or outside operating hours
    target_room = rooms[0]
    fixtures.append({
        "scenario_id": "NEG-005",
        "scenario_name": "Exam Outside Room Availability",
        "description": "Examination scheduled during facility maintenance closure window.",
        "target_room_code": target_room["room_code"],
        "target_room_id": target_room["id"],
        "closure_date": "2026-12-05",
        "closure_time": "08:00:00 to 18:00:00",
        "injected_anomaly": "Scheduling exam in ROOM-000001 on 2026-12-05 during facility shutdown",
        "expected_constraint_violated": "ROOM_UNAVAILABLE",
        "expected_reason_code": "ROOM_CLOSED_FOR_MAINTENANCE",
        "expected_outcome": "REJECTED_OR_FLAGGED_AS_CRITICAL",
    })

    return fixtures

