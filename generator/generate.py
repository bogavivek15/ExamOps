"""
ExamOps Deterministic Synthetic Data Generator
Generates realistic institutional data with fixed seed 20261022.
Supports --profile {starter, full}.
"""
import sys
import os
import argparse
import random
import uuid
from datetime import date, timedelta
from typing import Dict, List, Any

# Ensure generator package can import its modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generator.config import (
    FIXED_SEED,
    PROFILES,
    ACADEMIC_PERIOD,
    DEPARTMENTS,
    PROGRAMS,
    EQUIPMENT_CATALOG,
    FIRST_NAMES,
    LAST_NAMES,
)
from generator.negative_scenarios import generate_ground_truth_fixtures
from generator.exporters import export_all

def deterministic_uuid(seed_str: str) -> str:
    """Generates a reproducible UUID based on a deterministic seed string."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"examops.{seed_str}"))

def generate_dataset(profile_name: str = "full", seed: int = FIXED_SEED) -> Dict[str, Any]:
    """
    Main generation function.
    Strict topological order: Parents generated before dependent children.
    """
    rnd = random.Random(seed)
    profile = PROFILES.get(profile_name, PROFILES["full"])

    print(f"Generating ExamOps dataset: profile='{profile.name}', seed={seed}")
    print(f"Target metrics: {profile.student_count} students, {profile.exam_count} exams, "
          f"{profile.room_count} rooms, {profile.invigilator_count} invigilators")

    dataset: Dict[str, List[Dict[str, Any]]] = {}

    # --------------------------------------------------------------------------
    # 1. Academic Period
    # --------------------------------------------------------------------------
    period = dict(ACADEMIC_PERIOD)
    dataset["academic_periods"] = [period]
    period_id = period["id"]

    # --------------------------------------------------------------------------
    # 2. Students Master (Exactly student_count)
    # --------------------------------------------------------------------------
    students = []
    base_dob = date(2003, 1, 1)
    for i in range(1, profile.student_count + 1):
        s_code = f"STU-{i:06d}"
        f_name = rnd.choice(FIRST_NAMES)
        l_name = rnd.choice(LAST_NAMES)
        dob = base_dob + timedelta(days=rnd.randint(-700, 700))
        prog = rnd.choice(PROGRAMS)
        yos = rnd.randint(1, 4)
        students.append({
            "id": deterministic_uuid(s_code),
            "student_code": s_code,
            "first_name": f_name,
            "last_name": l_name,
            "email": f"{f_name.lower()}.{l_name.lower()}.{i:04d}@student.institution.edu",
            "date_of_birth": dob.isoformat(),
            "program": prog,
            "year_of_study": yos,
            "status": "ACTIVE",
        })
    dataset["students"] = students

    # --------------------------------------------------------------------------
    # 3. Invigilators Master (Exactly invigilator_count)
    # --------------------------------------------------------------------------
    invigilators = []
    for i in range(1, profile.invigilator_count + 1):
        inv_code = f"INV-{i:06d}"
        f_name = rnd.choice(FIRST_NAMES)
        l_name = rnd.choice(LAST_NAMES)
        dept = rnd.choice(DEPARTMENTS)
        invigilators.append({
            "id": deterministic_uuid(inv_code),
            "invigilator_code": inv_code,
            "first_name": f_name,
            "last_name": l_name,
            "email": f"inv.{f_name.lower()}.{l_name.lower()}.{i:03d}@staff.institution.edu",
            "department": dept,
            "max_hours_per_day": 8.00,
            "max_hours_per_week": 25.00,
            "status": "ACTIVE",
        })
    dataset["invigilators"] = invigilators

    # --------------------------------------------------------------------------
    # 4. User Profiles (Platform Admin, Academic Admins, Support, Instructors, Sample Learners)
    # --------------------------------------------------------------------------
    user_profiles = []
    # Superuser Platform Administrator
    user_profiles.append({
        "id": deterministic_uuid("usr-plat-admin-01"),
        "email": "admin@examops.institution.edu",
        "display_name": "Chief Platform Administrator",
        "role": "PLATFORM_ADMINISTRATOR",
        "student_id": None,
        "invigilator_id": None,
        "department": "Information Technology",
        "status": "ACTIVE",
    })
    # Operations Academic Administrators
    for i in (1, 2):
        user_profiles.append({
            "id": deterministic_uuid(f"usr-acad-admin-{i:02d}"),
            "email": f"exam.director.{i}@examops.institution.edu",
            "display_name": f"Operations Officer {i}",
            "role": "ACADEMIC_ADMINISTRATOR",
            "student_id": None,
            "invigilator_id": None,
            "department": "Examinations Office",
            "status": "ACTIVE",
        })
    # Support Staff
    for i in (1, 2):
        user_profiles.append({
            "id": deterministic_uuid(f"usr-support-{i:02d}"),
            "email": f"facilities.lead.{i}@examops.institution.edu",
            "display_name": f"Disability & Facilities Lead {i}",
            "role": "SUPPORT_STAFF",
            "student_id": None,
            "invigilator_id": None,
            "department": "Campus Facilities & Accessibility",
            "status": "ACTIVE",
        })
    # Instructors (1 per department)
    instructor_profiles = []
    for idx, dept in enumerate(DEPARTMENTS, 1):
        ip_id = deterministic_uuid(f"usr-instructor-{idx:02d}")
        prof = {
            "id": ip_id,
            "email": f"head.{dept.lower().split()[0]}@faculty.institution.edu",
            "display_name": f"Prof. {rnd.choice(LAST_NAMES)} ({dept})",
            "role": "INSTRUCTOR",
            "student_id": None,
            "invigilator_id": None,
            "department": dept,
            "status": "ACTIVE",
        }
        user_profiles.append(prof)
        instructor_profiles.append(prof)

    # Map sample invigilators to user profiles
    for i in range(min(10, len(invigilators))):
        inv = invigilators[i]
        user_profiles.append({
            "id": deterministic_uuid(f"usr-inv-{i:03d}"),
            "email": inv["email"],
            "display_name": f"{inv['first_name']} {inv['last_name']}",
            "role": "SUPPORT_STAFF",
            "student_id": None,
            "invigilator_id": inv["id"],
            "department": inv["department"],
            "status": "ACTIVE",
        })

    # Map sample students to user profiles (Learners)
    for i in range(min(20, len(students))):
        st = students[i]
        user_profiles.append({
            "id": deterministic_uuid(f"usr-stu-{i:04d}"),
            "email": st["email"],
            "display_name": f"{st['first_name']} {st['last_name']}",
            "role": "LEARNER",
            "student_id": st["id"],
            "invigilator_id": None,
            "department": None,
            "status": "ACTIVE",
        })
    dataset["user_profiles"] = user_profiles

    # --------------------------------------------------------------------------
    # 5. Courses Master
    # --------------------------------------------------------------------------
    courses = []
    course_code_idx = 1
    for dept in DEPARTMENTS:
        # Generate courses per department
        courses_in_dept = max(5, profile.course_count // len(DEPARTMENTS))
        for j in range(1, courses_in_dept + 1):
            if course_code_idx > profile.course_count:
                break
            c_code = f"CRS-{course_code_idx:06d}"
            c_name = f"{dept} Foundation & Applied Topics {j}"
            courses.append({
                "id": deterministic_uuid(c_code),
                "course_code": c_code,
                "name": c_name,
                "department": dept,
                "credits": rnd.choice([3, 4, 4, 5]),
                "academic_period_id": period_id,
                "status": "ACTIVE",
            })
            course_code_idx += 1
    dataset["courses"] = courses

    # --------------------------------------------------------------------------
    # 6. Course Instructors
    # --------------------------------------------------------------------------
    course_instructors = []
    for c in courses:
        inst = rnd.choice(instructor_profiles)
        course_instructors.append({
            "id": deterministic_uuid(f"ci-{c['course_code']}-{inst['id']}"),
            "course_id": c["id"],
            "instructor_profile_id": inst["id"],
            "role": "PRIMARY_INSTRUCTOR",
        })
    dataset["course_instructors"] = course_instructors

    # --------------------------------------------------------------------------
    # 7. Enrollments (Each student registered in min_courses to max_courses)
    # --------------------------------------------------------------------------
    enrollments = []
    enr_idx = 1
    student_course_map: Dict[str, List[str]] = {s["id"]: [] for s in students}
    course_student_map: Dict[str, List[str]] = {c["id"]: [] for c in courses}

    for s in students:
        num_courses = rnd.randint(profile.min_courses_per_student, profile.max_courses_per_student)
        chosen_courses = rnd.sample(courses, min(num_courses, len(courses)))
        for c in chosen_courses:
            enr_code = f"ENR-{enr_idx:06d}"
            enr = {
                "id": deterministic_uuid(enr_code),
                "enrollment_code": enr_code,
                "student_id": s["id"],
                "course_id": c["id"],
                "academic_period_id": period_id,
                "status": "ACTIVE",
            }
            enrollments.append(enr)
            student_course_map[s["id"]].append(c["id"])
            course_student_map[c["id"]].append(s["id"])
            enr_idx += 1
    dataset["enrollments"] = enrollments

    # --------------------------------------------------------------------------
    # 8. Examinations (Exactly exam_count)
    # --------------------------------------------------------------------------
    exams = []
    durations = [60, 90, 120, 120, 150, 180]
    for i in range(1, profile.exam_count + 1):
        ex_code = f"EXAM-2026-{i:06d}"
        c = courses[(i - 1) % len(courses)]
        dur = rnd.choice(durations)
        enrolled_count = len(course_student_map.get(c["id"], []))
        exams.append({
            "id": deterministic_uuid(ex_code),
            "exam_code": ex_code,
            "course_id": c["id"],
            "academic_period_id": period_id,
            "title": f"{c['name']} Comprehensive Examination",
            "exam_type": "FINAL",
            "duration_minutes": dur,
            "priority": rnd.choice([1, 2, 3, 3, 4, 5]),
            "status": "READY",
            "enrolled_student_count": enrolled_count,
        })
    dataset["exams"] = [{k: v for k, v in ex.items() if k != "enrolled_student_count"} for ex in exams]

    # --------------------------------------------------------------------------
    # 9. Exam Requirements
    # --------------------------------------------------------------------------
    exam_requirements = []
    req_idx = 1
    for ex in exams:
        # ~30% of exams require hardware or room features
        if rnd.random() < 0.35:
            req_code = f"REQ-{req_idx:06d}"
            eq = rnd.choice(EQUIPMENT_CATALOG)
            exam_requirements.append({
                "id": deterministic_uuid(req_code),
                "requirement_code": req_code,
                "exam_id": ex["id"],
                "requirement_type": "REQUIRED_EQUIPMENT",
                "value": eq["code"],
                "unit": "DEVICE",
                "is_mandatory": True,
            })
            req_idx += 1
    dataset["exam_requirements"] = exam_requirements

    # --------------------------------------------------------------------------
    # 10. Rooms Master (Exactly room_count)
    # --------------------------------------------------------------------------
    rooms = []
    buildings = [
        "Galileo Science Center",
        "Turing Computing Block",
        "Newton Hall of Physics",
        "Franklin Engineering Tower",
        "Curie Chemistry Pavilion",
        "Aristotle Arts & Humanities",
    ]
    for i in range(1, profile.room_count + 1):
        r_code = f"ROOM-{i:06d}"
        bldg = buildings[(i - 1) % len(buildings)]
        fl = ((i - 1) % 4) + 1
        is_acc = (rnd.random() < profile.accessible_room_rate)
        # Standard capacity distribution: large halls (100-200), medium (50-100), seminar (20-50)
        if i <= int(profile.room_count * 0.15):
            std_cap = rnd.randint(120, 200)
        elif i <= int(profile.room_count * 0.60):
            std_cap = rnd.randint(60, 110)
        else:
            std_cap = rnd.randint(25, 50)

        exam_cap = int(std_cap * rnd.uniform(0.50, 0.70))

        rooms.append({
            "id": deterministic_uuid(r_code),
            "room_code": r_code,
            "name": f"{bldg.split()[0]} Hall {fl}{i:02d}",
            "building": bldg,
            "floor": fl,
            "is_accessible": is_acc,
            "status": "AVAILABLE",
            "standard_capacity": std_cap,
            "exam_capacity": exam_cap,
        })
    dataset["rooms"] = [{k: v for k, v in r.items() if k not in ("standard_capacity", "exam_capacity")} for r in rooms]

    # --------------------------------------------------------------------------
    # 11. Room Capacities
    # --------------------------------------------------------------------------
    room_capacities = []
    for r in rooms:
        cap_code = f"CAP-{len(room_capacities) + 1:06d}"
        room_capacities.append({
            "id": deterministic_uuid(cap_code),
            "capacity_code": cap_code,
            "room_id": r["id"],
            "standard_capacity": r["standard_capacity"],
            "exam_capacity": r["exam_capacity"],
            "effective_start": period["start_date"],
            "effective_end": period["end_date"],
        })
    dataset["room_capacities"] = room_capacities

    # --------------------------------------------------------------------------
    # 12. Equipment Types & 13. Room Equipment
    # --------------------------------------------------------------------------
    equipment_types = []
    for eq in EQUIPMENT_CATALOG:
        equipment_types.append({
            "id": deterministic_uuid(f"eq-type-{eq['code']}"),
            "code": eq["code"],
            "name": eq["name"],
            "category": eq["category"],
        })
    dataset["equipment_types"] = equipment_types

    room_equipment = []
    for r in rooms:
        # Every room has a projector
        proj_type = equipment_types[0]
        room_equipment.append({
            "id": deterministic_uuid(f"re-{r['room_code']}-{proj_type['code']}"),
            "room_id": r["id"],
            "equipment_type_id": proj_type["id"],
            "quantity": 1,
            "status": "OPERATIONAL",
        })
        # If accessible, add ACCESSIBLE_DESK
        if r["is_accessible"]:
            acc_desk = equipment_types[2]
            room_equipment.append({
                "id": deterministic_uuid(f"re-{r['room_code']}-{acc_desk['code']}"),
                "room_id": r["id"],
                "equipment_type_id": acc_desk["id"],
                "quantity": rnd.randint(2, 6),
                "status": "OPERATIONAL",
            })
        # Computing block rooms have PCs
        if "Computing" in r["building"]:
            comp_lab = equipment_types[1]
            room_equipment.append({
                "id": deterministic_uuid(f"re-{r['room_code']}-{comp_lab['code']}"),
                "room_id": r["id"],
                "equipment_type_id": comp_lab["id"],
                "quantity": r["exam_capacity"],
                "status": "OPERATIONAL",
            })
    dataset["room_equipment"] = room_equipment

    # --------------------------------------------------------------------------
    # 14. Room Availabilities (Operating windows 08:00 - 18:00; Mon-Sat)
    # --------------------------------------------------------------------------
    room_availabilities = []
    for r in rooms:
        # Active operating window Monday through Saturday (0 = Mon, 5 = Sat)
        for dow in range(6):
            ra_id = deterministic_uuid(f"ra-{r['room_code']}-dow-{dow}")
            room_availabilities.append({
                "id": ra_id,
                "room_id": r["id"],
                "day_of_week": dow,
                "specific_date": None,
                "start_time": "08:00:00",
                "end_time": "18:00:00",
                "availability_type": "AVAILABLE",
                "effective_start": period["exam_start_date"],
                "effective_end": period["exam_end_date"],
                "reason": "Standard Academic Operating Window",
            })

    # Add one scheduled maintenance closure to ROOM-000001 (Fixture for Negative Scenario 5)
    target_r1 = rooms[0]
    room_availabilities.append({
        "id": deterministic_uuid("ra-closure-room-01"),
        "room_id": target_r1["id"],
        "day_of_week": None,
        "specific_date": "2026-12-05",
        "start_time": "08:00:00",
        "end_time": "18:00:00",
        "availability_type": "CLOSED",
        "effective_start": "2026-12-05",
        "effective_end": "2026-12-05",
        "reason": "HVAC Scheduled Duct Cleaning & Electrical Inspection",
    })
    dataset["room_availabilities"] = room_availabilities

    # --------------------------------------------------------------------------
    # 15. Invigilator Availabilities (Standard shifts across exam period)
    # --------------------------------------------------------------------------
    availabilities = []
    avl_idx = 1
    for inv in invigilators:
        # Each invigilator available on weekday shifts
        for dow in range(6):
            avl_code = f"AVL-{avl_idx:06d}"
            availabilities.append({
                "id": deterministic_uuid(avl_code),
                "availability_code": avl_code,
                "invigilator_id": inv["id"],
                "day_of_week": dow,
                "specific_date": None,
                "start_time": "08:00:00",
                "end_time": "18:00:00",
                "availability_type": "AVAILABLE",
                "effective_start": period["exam_start_date"],
                "effective_end": period["exam_end_date"],
            })
            avl_idx += 1
    dataset["availabilities"] = availabilities

    # --------------------------------------------------------------------------
    # 16. Accommodations (~6% of students) & 17. Accommodation Notes
    # --------------------------------------------------------------------------
    accommodations = []
    accommodation_notes = []
    acc_types = ["EXTENDED_TIME", "ACCESSIBLE_ROOM", "LOW_DISTRACTION", "SPECIAL_EQUIPMENT"]
    acc_idx = 1

    for s in students:
        if rnd.random() < profile.accommodation_rate:
            acc_code = f"ACO-{acc_idx:06d}"
            a_type = rnd.choice(acc_types)
            extra_min = 30 if a_type == "EXTENDED_TIME" else None
            extra_pct = 25.00 if (a_type == "EXTENDED_TIME" and rnd.random() < 0.5) else None
            req_feat = "WHEELCHAIR_ACCESSIBLE" if a_type == "ACCESSIBLE_ROOM" else None
            req_eq = "ADJUSTABLE_DESK" if a_type == "SPECIAL_EQUIPMENT" else None

            acc_id = deterministic_uuid(acc_code)
            accommodations.append({
                "id": acc_id,
                "accommodation_code": acc_code,
                "student_id": s["id"],
                "accommodation_type": a_type,
                "extra_time_minutes": extra_min,
                "extra_time_percentage": extra_pct,
                "required_room_feature": req_feat,
                "required_equipment": req_eq,
                "is_active": True,
                "effective_start": period["start_date"],
                "effective_end": period["end_date"],
            })

            # Confidential medical notes
            accommodation_notes.append({
                "id": deterministic_uuid(f"acn-{acc_code}"),
                "accommodation_id": acc_id,
                "clinical_notes": f"Verified accessibility plan on file with Disability Services for {s['first_name']} {s['last_name']}.",
                "approved_by": user_profiles[1]["id"], # Operations Officer 1
                "documentation_url": f"https://disability.institution.edu/records/doc_{acc_code}.pdf",
            })
            acc_idx += 1

    dataset["accommodations"] = accommodations
    dataset["accommodation_notes"] = accommodation_notes

    # --------------------------------------------------------------------------
    # 18. Generate Labelled Negative Fixtures (Ground Truth)
    # --------------------------------------------------------------------------
    ground_truth = generate_ground_truth_fixtures(
        students=students,
        exams=exams,
        rooms=rooms,
        invigilators=invigilators,
        accommodations=accommodations,
        room_availabilities=room_availabilities,
    )

    return dataset, ground_truth

def main():
    parser = argparse.ArgumentParser(description="ExamOps Deterministic Synthetic Data Generator")
    parser.add_argument("--profile", choices=["starter", "full"], default="full", help="Data volume profile")
    parser.add_argument("--seed", type=int, default=FIXED_SEED, help="Fixed random seed (default: 20261022)")
    parser.add_argument("--output", default="data", help="Output base directory")
    args = parser.parse_args()

    dataset, ground_truth = generate_dataset(profile_name=args.profile, seed=args.seed)
    manifest = export_all(dataset, ground_truth, output_base_dir=args.output)

    print("\nGeneration completed successfully!")
    print("Exported Entities Summary:")
    for entity, count in manifest["entity_counts"].items():
        print(f"  - {entity}: {count} records")
    print(f"  - ground_truth: {len(ground_truth)} negative fixtures")
    print(f"\nManifest and canonical digests stored in '{args.output}/manifest.json'.")

if __name__ == "__main__":
    main()
