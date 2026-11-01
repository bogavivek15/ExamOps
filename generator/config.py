"""
ExamOps Synthetic Data Generation Configuration
Defines generation parameters, fixed seed, profiles, and institutional constraints.
"""
from dataclasses import dataclass
from typing import Dict, Any

FIXED_SEED = 20261022

@dataclass(frozen=True)
class ProfileConfig:
    name: str
    student_count: int
    exam_count: int
    room_count: int
    invigilator_count: int
    course_count: int
    min_courses_per_student: int
    max_courses_per_student: int
    accommodation_rate: float
    accessible_room_rate: float

PROFILES: Dict[str, ProfileConfig] = {
    "starter": ProfileConfig(
        name="starter",
        student_count=500,
        exam_count=30,
        room_count=10,
        invigilator_count=20,
        course_count=25,
        min_courses_per_student=3,
        max_courses_per_student=5,
        accommodation_rate=0.06,
        accessible_room_rate=0.25,
    ),
    "full": ProfileConfig(
        name="full",
        student_count=5000,
        exam_count=300,
        room_count=100,
        invigilator_count=200,
        course_count=150,
        min_courses_per_student=4,
        max_courses_per_student=6,
        accommodation_rate=0.06,
        accessible_room_rate=0.20,
    ),
}

# Institutional Parameters
ACADEMIC_PERIOD = {
    "id": "11111111-1111-1111-1111-111111111111",
    "code": "TERM-2026-02",
    "name": "Fall 2026 Examination Period",
    "start_date": "2026-09-01",
    "end_date": "2026-12-31",
    "exam_start_date": "2026-12-01",
    "exam_end_date": "2026-12-14",
    "is_active": True,
}

DEPARTMENTS = [
    "Computer Science",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Mathematics & Statistics",
    "Physics",
    "Chemistry",
    "Biological Sciences",
    "Economics & Finance",
    "Business Administration",
    "Humanities & Social Sciences",
]

PROGRAMS = [
    "B.S. Computer Science",
    "B.S. Software Engineering",
    "B.S. Data Science",
    "B.S. Electrical Engineering",
    "B.S. Mechanical Engineering",
    "B.S. Mathematics",
    "B.S. Applied Physics",
    "B.A. Economics",
    "B.B.A. Business Administration",
    "B.S. Biotechnology",
]

EQUIPMENT_CATALOG = [
    {"code": "PROJECTOR", "name": "High-Definition Ceiling Projector", "category": "AV"},
    {"code": "COMPUTING_LAB", "name": "Standard PC Lab Workstations", "category": "COMPUTING"},
    {"code": "ACCESSIBLE_DESK", "name": "Height-Adjustable Accessible Examination Desk", "category": "ACCESSIBILITY"},
    {"code": "AUDIO_SYSTEM", "name": "Voice Amplification Sound System", "category": "AV"},
    {"code": "LAB_MICROSCOPE", "name": "Digital Inspection Microscope", "category": "LABORATORY"},
]

FIRST_NAMES = [
    "Aarav", "Aditi", "Alexander", "Amara", "Carlos", "Chloe", "David", "Elena", "Ethan", "Fatima",
    "Gabriel", "Grace", "Hannah", "Hassan", "Ishaan", "Isabella", "James", "Jasmine", "John", "Kavita",
    "Liam", "Lucas", "Maya", "Mei", "Michael", "Noah", "Olivia", "Priya", "Rahul", "Rohan",
    "Samuel", "Sarah", "Sophia", "Tariq", "Vikram", "William", "Yuki", "Zara", "Benjamin", "Zoe"
]

LAST_NAMES = [
    "Agarwal", "Anderson", "Brown", "Chen", "Das", "Davis", "Garcia", "Gupta", "Hernandez", "Iyer",
    "Johnson", "Jones", "Kapoor", "Kim", "Kumar", "Lee", "Martin", "Miller", "Nair", "Patel",
    "Rao", "Rodriguez", "Sharma", "Singh", "Smith", "Taylor", "Thomas", "Verma", "Wang", "Williams",
    "Wilson", "Wright", "Yamamoto", "Zhang", "Al-Mansoor", "O'Connor", "Dubois", "Muller", "Tanaka", "Sato"
]

