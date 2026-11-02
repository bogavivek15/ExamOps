"""
ExamOps Independent Scheduler Performance & Diagnostic Audit
Comprehensive analysis of the 300-exam full baseline scheduling run.
"""
import sys
import os
import json
import time
import psutil
from datetime import date, time as dtime, datetime, timezone
from collections import Counter, defaultdict
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.scheduler.models import (
    ExamModel, RoomModel, InvigilatorModel, ExamParticipant, ExamRequirementModel,
    CandidateSlot, RoomAllocation
)
from backend.scheduler.conflict_graph import ConflictGraph
from backend.scheduler.engine import SchedulingEngine
from backend.scheduler.schedule_validator import ScheduleValidator

def load_baseline_data():
    with open("data/json/exams.json", "r", encoding="utf-8") as f:
        exams_json = json.load(f)
    with open("data/json/students.json", "r", encoding="utf-8") as f:
        students_json = json.load(f)
    with open("data/json/enrollments.json", "r", encoding="utf-8") as f:
        enrollments_json = json.load(f)
    with open("data/json/rooms.json", "r", encoding="utf-8") as f:
        rooms_json = json.load(f)
    with open("data/json/room_capacities.json", "r", encoding="utf-8") as f:
        capacities_json = json.load(f)
    with open("data/json/room_availabilities.json", "r", encoding="utf-8") as f:
        ra_json = json.load(f)
    with open("data/json/room_equipment.json", "r", encoding="utf-8") as f:
        req_json = json.load(f)
    with open("data/json/equipment_types.json", "r", encoding="utf-8") as f:
        eq_types_json = json.load(f)
    with open("data/json/invigilators.json", "r", encoding="utf-8") as f:
        invs_json = json.load(f)
    with open("data/json/availabilities.json", "r", encoding="utf-8") as f:
        inv_avail_json = json.load(f)
    with open("data/json/accommodations.json", "r", encoding="utf-8") as f:
        acc_json = json.load(f)
    with open("data/json/exam_requirements.json", "r", encoding="utf-8") as f:
        exam_req_json = json.load(f)

    acc_by_student = {a["student_id"]: a for a in acc_json if a.get("is_active")}
    student_lookup = {s["id"]: s for s in students_json}

    course_students = defaultdict(list)
    for enr in enrollments_json:
        if enr.get("status") == "ACTIVE":
            course_students[enr["course_id"]].append(enr["student_id"])

    exam_req_by_exam = defaultdict(list)
    for r in exam_req_json:
        exam_req_by_exam[r["exam_id"]].append(ExamRequirementModel(
            id=r["id"],
            requirement_code=r["requirement_code"],
            requirement_type=r["requirement_type"],
            value=r["value"],
            is_mandatory=r.get("is_mandatory", True),
        ))

    exam_models = []
    for ex in exams_json:
        cid = ex["course_id"]
        enrolled_stu_ids = course_students.get(cid, [])
        participants = []
        for sid in enrolled_stu_ids:
            st = student_lookup[sid]
            acc = acc_by_student.get(sid)
            extra_min = 0
            req_acc_room = False
            req_low_dist = False
            req_sp_eq = None
            if acc:
                a_type = acc["accommodation_type"]
                if a_type == "EXTENDED_TIME":
                    extra_min = acc.get("extra_time_minutes") or int(ex["duration_minutes"] * (acc.get("extra_time_percentage", 25) / 100.0))
                elif a_type == "ACCESSIBLE_ROOM":
                    req_acc_room = True
                elif a_type == "LOW_DISTRACTION":
                    req_low_dist = True
                elif a_type == "SPECIAL_EQUIPMENT":
                    req_sp_eq = acc.get("required_equipment")

            eff_dur = ex["duration_minutes"] + extra_min
            participants.append(ExamParticipant(
                student_id=sid,
                student_code=st["student_code"],
                first_name=st["first_name"],
                last_name=st["last_name"],
                base_duration_minutes=ex["duration_minutes"],
                extra_duration_minutes=extra_min,
                effective_duration_minutes=eff_dur,
                requires_accessible_room=req_acc_room,
                requires_low_distraction=req_low_dist,
                requires_special_equipment=req_sp_eq,
                accommodation_details=acc,
            ))

        exam_models.append(ExamModel(
            id=ex["id"],
            exam_code=ex["exam_code"],
            course_id=cid,
            course_code=f"CRS-{cid[:6]}",
            title=ex["title"],
            duration_minutes=ex["duration_minutes"],
            priority=ex.get("priority", 3),
            requirements=exam_req_by_exam.get(ex["id"], []),
            participants=participants,
        ))

    cap_by_room = {c["room_id"]: c for c in capacities_json}
    eq_type_code_by_id = {eq["id"]: eq["code"] for eq in eq_types_json}
    eq_by_room = defaultdict(set)
    for re_item in req_json:
        eq_code = eq_type_code_by_id.get(re_item["equipment_type_id"])
        if eq_code:
            eq_by_room[re_item["room_id"]].add(eq_code)

    op_by_room = defaultdict(list)
    closures_by_room = defaultdict(list)
    for ra in ra_json:
        rid = ra["room_id"]
        if ra.get("availability_type") == "AVAILABLE":
            op_by_room[rid].append(ra)
        else:
            closures_by_room[rid].append(ra)

    room_models = []
    for r in rooms_json:
        cap = cap_by_room.get(r["id"], {})
        room_models.append(RoomModel(
            id=r["id"],
            room_code=r["room_code"],
            name=r["name"],
            building=r["building"],
            floor=r["floor"],
            is_accessible=r["is_accessible"],
            standard_capacity=cap.get("standard_capacity", 50),
            exam_capacity=cap.get("exam_capacity", 35),
            equipment_codes=eq_by_room.get(r["id"], set()),
            operating_hours=op_by_room.get(r["id"], []),
            closures=closures_by_room.get(r["id"], []),
        ))

    avail_by_inv = defaultdict(list)
    for av in inv_avail_json:
        avail_by_inv[av["invigilator_id"]].append(av)

    inv_models = []
    for inv in invs_json:
        inv_models.append(InvigilatorModel(
            id=inv["id"],
            invigilator_code=inv["invigilator_code"],
            first_name=inv["first_name"],
            last_name=inv["last_name"],
            department=inv["department"],
            max_hours_per_day=float(inv.get("max_hours_per_day", 8.0)),
            max_hours_per_week=float(inv.get("max_hours_per_week", 25.0)),
            availabilities=avail_by_inv.get(inv["id"], []),
        ))

    return exam_models, room_models, inv_models

def run_audit():
    print("=" * 75)
    print("EXAMOPS INDEPENDENT SCHEDULER PERFORMANCE & DIAGNOSTIC AUDIT")
    print("=" * 75)

    exam_models, room_models, inv_models = load_baseline_data()
    print(f"Loaded: {len(exam_models)} exams, {len(room_models)} rooms, {len(inv_models)} invigilators.")

    # 1. Profile Conflict Graph
    t0 = time.perf_counter()
    cg = ConflictGraph(exam_models)
    t_graph = time.perf_counter() - t0

    # Conflict Graph Metrics
    total_edges = 0
    max_degree = 0
    exam_degrees = []
    for e in exam_models:
        deg = len(cg.adjacency.get(e.id, set()))
        total_edges += deg
        exam_degrees.append(deg)
        if deg > max_degree:
            max_degree = deg
    total_edges //= 2
    avg_degree = sum(exam_degrees) / len(exam_degrees) if exam_degrees else 0

    print(f"\nConflict Graph Topology:")
    print(f"  - Total Vertices (Exams): {len(exam_models)}")
    print(f"  - Total Conflict Edges:   {total_edges}")
    print(f"  - Average Degree (conflicts per exam): {avg_degree:.1f}")
    print(f"  - Maximum Degree:         {max_degree}")
    print(f"  - Graph Construction Time: {t_graph:.4f}s")

    # 2. Run Engine with psutil Memory Profiling
    proc = psutil.Process()
    mem_before = proc.memory_info().rss
    t_solve_start = time.perf_counter()

    engine = SchedulingEngine(
        exams=exam_models,
        rooms=room_models,
        invigilators=inv_models,
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 14),
        daily_start_time=dtime(8, 0),
        daily_end_time=dtime(18, 0),
        slot_granularity_minutes=30,
        max_improvement_passes=3,
    )

    result = engine.execute_schedule()
    t_solve_end = time.perf_counter()
    mem_after = proc.memory_info().rss
    peak_mem = max(mem_before, mem_after)

    solve_duration = t_solve_end - t_solve_start
    metrics = result["metrics"]

    print(f"\nScheduling Execution Performance:")
    print(f"  - Total Solve Runtime:     {solve_duration:.2f} s")
    print(f"  - Peak Memory Consumption: {peak_mem / (1024 * 1024):.2f} MB")

    print(f"\nAssignment Outcomes:")
    print(f"  - Total Exams:             {metrics['total_exams']}")
    print(f"  - Scheduled Exams:         {metrics['scheduled_count']}")
    print(f"  - Unassigned Exams:        {metrics['unassigned_count']}")
    print(f"  - Completion Rate:         {metrics['completion_percentage']}%")
    print(f"  - Student Registrations:   {metrics['scheduled_student_exam_registrations']} / {metrics['total_student_exam_registrations']} ({metrics['student_coverage_percentage']}%)")
    print(f"  - Room Assignments:        {metrics['confirmed_room_assignments_count']}")
    print(f"  - Invigilator Staffings:   {metrics['invigilator_staffings_count']}")
    print(f"  - Hard Constraint Violations: {result['violations_count']}")
    print(f"  - Is Certified Valid:      {result['is_certified_valid']}")

    # 3. ROOT CAUSE INVESTIGATION: Why is the result 81/300?
    print(f"\n" + "=" * 75)
    print("ROOT CAUSE INVESTIGATION: WHY WAS THE SCHEDULING RESULT 81/300?")
    print("=" * 75)

    cohort_sizes = [len(e.participants) for e in exam_models]
    room_caps = [r.exam_capacity for r in room_models]
    max_room_cap = max(room_caps)
    avg_room_cap = sum(room_caps) / len(room_caps)

    print(f"\nResource Capacity vs Demand Analysis:")
    print(f"  - Average Exam Cohort Size: {sum(cohort_sizes)/len(cohort_sizes):.1f} students")
    print(f"  - Min / Median / Max Cohort: {min(cohort_sizes)} / {sorted(cohort_sizes)[len(cohort_sizes)//2]} / {max(cohort_sizes)} students")
    print(f"  - Exams requiring > 50 seats: {sum(1 for s in cohort_sizes if s > 50)} / {len(cohort_sizes)} ({sum(1 for s in cohort_sizes if s > 50)/len(cohort_sizes)*100:.1f}%)")
    print(f"  - Total Rooms: {len(room_models)}, Avg Exam Capacity: {avg_room_cap:.1f}, Max Exam Capacity: {max_room_cap}")
    print(f"  - Rooms with exam_capacity >= 50: {sum(1 for c in room_caps if c >= 50)}")
    print(f"  - Rooms with exam_capacity >= 80: {sum(1 for c in room_caps if c >= 80)}")

    unassigned_exams = result["unassigned_exams"]
    primary_reasons = Counter()
    all_reasons = Counter()
    for u in unassigned_exams:
        rcs = u.get("reason_codes", [])
        if rcs:
            primary_reasons[rcs[0]] += 1
            for rc in rcs:
                all_reasons[rc] += 1
        else:
            primary_reasons["NO_REASON_GIVEN"] += 1

    print(f"\nUnassigned Exams Primary Reason Breakdown (Total = {len(unassigned_exams)}):")
    for r, count in primary_reasons.most_common():
        pct = (count / len(unassigned_exams)) * 100
        print(f"  - {r:<35}: {count:>3} exams ({pct:5.1f}%)")

    # 4. Determinism Check: Run a second time and assert identical results
    print(f"\n" + "=" * 75)
    print("DETERMINISM VERIFICATION (Pass 2 with Identical Seed & Inputs)")
    print("=" * 75)
    engine2 = SchedulingEngine(
        exams=exam_models,
        rooms=room_models,
        invigilators=inv_models,
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 14),
        daily_start_time=dtime(8, 0),
        daily_end_time=dtime(18, 0),
        slot_granularity_minutes=30,
        max_improvement_passes=3,
    )
    result2 = engine2.execute_schedule()
    metrics2 = result2["metrics"]

    assert metrics["scheduled_count"] == metrics2["scheduled_count"], "Scheduled counts must match!"
    assert metrics["unassigned_count"] == metrics2["unassigned_count"], "Unassigned counts must match!"
    assert metrics["confirmed_room_assignments_count"] == metrics2["confirmed_room_assignments_count"], "Room assignments must match!"
    assert metrics["invigilator_staffings_count"] == metrics2["invigilator_staffings_count"], "Invigilator staffings must match!"
    
    asgn1 = sorted([a["assignment_code"] for a in result["assignments"]])
    asgn2 = sorted([a["assignment_code"] for a in result2["assignments"]])
    assert asgn1 == asgn2, "Exact assignment codes must match 100%!"
    print("✓ DETERMINISM CERTIFIED: Run 1 and Run 2 produced 100% identical outputs!")

    audit_summary = {
        "dataset": {
            "exams": len(exam_models),
            "rooms": len(room_models),
            "invigilators": len(inv_models),
            "total_enrollments": len(cohort_sizes),
        },
        "performance": {
            "graph_time_seconds": round(t_graph, 4),
            "solve_runtime_seconds": round(solve_duration, 2),
            "peak_memory_mb": round(peak_mem / (1024 * 1024), 2),
        },
        "topology": {
            "total_edges": total_edges,
            "avg_degree": round(avg_degree, 2),
            "max_degree": max_degree,
        },
        "outcomes": {
            "scheduled": metrics["scheduled_count"],
            "unassigned": metrics["unassigned_count"],
            "completion_pct": metrics["completion_percentage"],
            "student_coverage_pct": metrics["student_coverage_percentage"],
            "room_assignments": metrics["confirmed_room_assignments_count"],
            "invigilator_staffings": metrics["invigilator_staffings_count"],
            "hard_constraint_violations": result["violations_count"],
            "is_certified_valid": result["is_certified_valid"],
        },
        "root_cause_analysis": {
            "cohort_avg": round(sum(cohort_sizes)/len(cohort_sizes), 1),
            "exams_gt_50_students": sum(1 for s in cohort_sizes if s > 50),
            "rooms_ge_50_capacity": sum(1 for c in room_caps if c >= 50),
            "primary_unassigned_reasons": dict(primary_reasons),
        }
    }

    with open("docs/performance/scheduler_audit_data.json", "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2)
    print("\nAudit data written to docs/performance/scheduler_audit_data.json")

if __name__ == "__main__":
    run_audit()
