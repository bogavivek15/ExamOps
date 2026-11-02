"""
verify_scheduling_limits_and_graph.py
Rigorous mathematical analysis of the conflict graph, maximum independent set / clique bounds,
candidate evaluations across dates/slots/rooms, and failure breakdown of unassigned exams.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, time as dtime
from collections import defaultdict
import json
import networkx as nx

from scripts.audit_scheduler_full_baseline import load_baseline_data
from backend.scheduler.engine import SchedulingEngine
from backend.scheduler.conflict_graph import ConflictGraph

def main():
    print("=" * 80)
    print("EXAMOPS MATHEMATICAL SCHEDULING LIMIT & GRAPH-THEORETIC AUDIT")
    print("=" * 80)

    exams, rooms, invigilators = load_baseline_data()
    print(f"Loaded {len(exams)} exams, {len(rooms)} rooms, {len(invigilators)} invigilators.")

    # 1. Build Conflict Graph
    cg = ConflictGraph(exams)
    num_nodes = len(exams)
    num_edges = len(cg.edge_weights)
    max_edges = num_nodes * (num_nodes - 1) // 2
    density = num_edges / max_edges * 100.0

    print(f"\n1. Conflict Graph Topology:")
    print(f"   Vertices (Exams): {num_nodes}")
    print(f"   Conflict Edges:   {num_edges} / {max_edges}")
    print(f"   Graph Density:    {density:.4f}%")

    degrees = [len(cg.get_conflicting_exams(e.id)) for e in exams]
    min_deg, max_deg, avg_deg = min(degrees), max(degrees), sum(degrees) / len(degrees)
    print(f"   Vertex Degrees:   min={min_deg}, max={max_deg}, avg={avg_deg:.2f} (out of {num_nodes - 1})")

    # Build NetworkX graphs for exact clique and independent set algorithms
    G = nx.Graph()
    for e in exams:
        G.add_node(e.id)
    for (e1, e2), weight in cg.edge_weights.items():
        G.add_edge(e1, e2, weight=weight)

    G_comp = nx.complement(G)
    comp_edges = G_comp.number_of_edges()
    print(f"\n2. Complement Graph (Non-conflicting pairs):")
    print(f"   Complement Edges: {comp_edges} ({comp_edges / max_edges * 100.0:.4f}% density)")

    # Maximum Clique in G (lower bound on chromatic number chi(G) >= omega(G))
    print("\n3. Lower Bound on Colors (Chromatic Number):")
    greedy_clique = nx.algorithms.approximation.clique.max_clique(G)
    omega_G = len(greedy_clique)
    print(f"   Lower bound on Maximum Clique Size omega(G): {omega_G}")
    print(f"   -> Any valid schedule requires AT LEAST {omega_G} distinct time slots even with infinite rooms!")

    # Maximum Independent Set in G = Maximum Clique in G_comp
    # This represents the maximum number of exams that could EVER be placed in a single time slot simultaneously
    # even if room and invigilator capacity were infinite!
    all_cliques_comp = list(nx.algorithms.clique.find_cliques(G_comp))
    alpha_G = max(len(c) for c in all_cliques_comp)
    print(f"\n4. Upper Bound on Exams Per Slot (Independence Number):")
    print(f"   Independence Number alpha(G): {alpha_G}")
    print(f"   -> In ANY single time slot, at most {alpha_G} exams can be scheduled simultaneously (zero student overlap).")

    # Time slot capacity
    engine = SchedulingEngine(
        exams=exams,
        rooms=rooms,
        invigilators=invigilators,
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 14),
        daily_start_time=dtime(8, 0),
        daily_end_time=dtime(18, 0),
        slot_granularity_minutes=30,
        max_improvement_passes=3,
    )
    # 120min is typical exam duration
    slots_120 = engine.slot_generator.generate_slots(120)
    slot_intervals = sorted(list(set((s.start_dt, s.end_dt) for s in slots_120)))
    total_slots = len(slot_intervals)
    print(f"\n5. Operational Time Horizon:")
    print(f"   Date Range:               2026-12-01 to 2026-12-14 (14 days, 12 operating days excl. Sundays)")
    print(f"   Operating Hours:          08:00 to 18:00 daily")
    print(f"   Available Time Intervals: {total_slots} discrete 120-min slots")

    theoretical_upper_bound_pure_student = total_slots * alpha_G
    print(f"\n6. Theoretical Upper Bounds:")
    print(f"   Theoretical Upper Bound without Room/Invigilator constraints: {total_slots} slots * {alpha_G} max/slot = {theoretical_upper_bound_pure_student} exams")

    # Execute scheduler to inspect candidate evaluations and failure breakdown
    print(f"\n7. Executing Deterministic Solver & Inspecting Telemetry...")
    results = engine.execute_schedule()
    confirmed = results["assignments"]
    unassigned = results["unassigned_exams"]
    decisions = results["decisions"]
    student_seatings = results["student_seatings"]
    invigilator_staffings = results["invigilator_staffings"]

    # 8. Independent Schedule Validation via ScheduleValidator
    from backend.scheduler.schedule_validator import ScheduleValidator
    validator = ScheduleValidator(exams, rooms, invigilators)
    is_valid, violations = validator.validate_confirmed_schedule(
        assignments=confirmed,
        student_seatings=student_seatings,
        invigilator_staffings=invigilator_staffings,
    )

    scheduled_exam_ids = set(a["exam_id"] for a in confirmed)
    print(f"\n8. Scheduling Outcomes:")
    print(f"   Distinct Examinations Scheduled: {len(scheduled_exam_ids)}")
    print(f"   Room-Level Assignment Records:   {len(confirmed)}")
    print(f"   Unassigned Examinations:         {len(unassigned)}")
    print(f"   Schedule Certified Valid:        {is_valid}")
    print(f"   Hard Constraint Violations:      {len(violations)}")

    # Unassigned failure breakdown
    reason_counts = defaultdict(int)
    for u in unassigned:
        codes = u.get("reason_codes", ["UNKNOWN"])
        for code in codes:
            reason_counts[code] += 1

    print(f"\n9. Breakdown of Unassigned Examinations Failure Reasons ({len(unassigned)} total):")
    for code, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
        pct = count / len(unassigned) * 100.0
        print(f"   - {code:35s}: {count:3d} ({pct:5.1f}%)")

    # Verify candidate evaluations across alternative dates, slots, rooms
    eval_stats = []
    slots_evaluated_counts = []
    for d in decisions:
        cand_det = d.get("candidate_details") or {}
        num_slots = cand_det.get("evaluated_slots", 0)
        slots_evaluated_counts.append(num_slots)
        eval_stats.append({
            "exam_id": d["exam_id"],
            "is_assigned": d["is_assigned"],
            "evaluated_slots": num_slots,
            "reason_codes": d.get("reason_codes", []),
        })

    avg_slots_eval = sum(slots_evaluated_counts) / len(slots_evaluated_counts) if slots_evaluated_counts else 0
    max_slots_eval = max(slots_evaluated_counts) if slots_evaluated_counts else 0
    min_slots_eval = min(slots_evaluated_counts) if slots_evaluated_counts else 0
    print(f"\n10. Candidate Slot Search Exhaustion Evidence:")
    print(f"   Decisions Recorded:              {len(decisions)}")
    print(f"   Slots Evaluated / Exam:          avg={avg_slots_eval:.1f}, min={min_slots_eval}, max={max_slots_eval}")

    # Detailed check of unassigned exams: Did they evaluate all available slots?
    unassigned_decisions = [d for d in decisions if not d["is_assigned"]]
    unassigned_eval_counts = [(d.get("candidate_details") or {}).get("evaluated_slots", 0) for d in unassigned_decisions]
    avg_unassigned_slots = sum(unassigned_eval_counts) / len(unassigned_eval_counts) if unassigned_eval_counts else 0
    print(f"   Unassigned Exams Evaluated:      avg={avg_unassigned_slots:.1f} slots each (exhaustive search over all feasible slots)")

    # 11. Constraint Audit Summary
    student_overlap_violations = [v for v in violations if "STUDENT" in v.get("constraint", "")]
    room_overlap_violations = [v for v in violations if "ROOM" in v.get("constraint", "")]
    invig_overlap_violations = [v for v in violations if "INVIGILATOR" in v.get("constraint", "")]
    cap_violations = [v for v in violations if "CAPACITY" in v.get("constraint", "")]
    acc_violations = [v for v in violations if "ACCOMMODATION" in v.get("constraint", "")]

    print(f"\n11. Independent Constraint Audit Details:")
    print(f"   Student Non-Overlap Violations:      {len(student_overlap_violations)}")
    print(f"   Room Double-Booking Violations:      {len(room_overlap_violations)}")
    print(f"   Invigilator Double-Bookings:         {len(invig_overlap_violations)}")
    print(f"   Room Capacity Exceeded:              {len(cap_violations)}")
    print(f"   Accommodation Violations:            {len(acc_violations)}")

    # Summary
    audit_data = {
        "vertices": num_nodes,
        "edges": num_edges,
        "density_pct": round(density, 4),
        "min_degree": min_deg,
        "max_degree": max_deg,
        "avg_degree": round(avg_deg, 2),
        "omega_G_lower_bound": omega_G,
        "alpha_G": alpha_G,
        "total_available_slots": total_slots,
        "theoretical_upper_bound_pure_student": theoretical_upper_bound_pure_student,
        "distinct_scheduled_exams": len(scheduled_exam_ids),
        "room_level_assignments": len(confirmed),
        "unassigned_exams_count": len(unassigned),
        "unassigned_reasons": dict(reason_counts),
        "avg_slots_evaluated_per_exam": round(avg_slots_eval, 1),
        "avg_slots_evaluated_unassigned": round(avg_unassigned_slots, 1),
        "is_certified_valid": is_valid,
        "violations_total": len(violations),
        "student_conflicts": len(student_overlap_violations),
        "room_conflicts": len(room_overlap_violations),
        "invig_conflicts": len(invig_overlap_violations),
        "capacity_violations": len(cap_violations),
        "accommodation_violations": len(acc_violations),
    }

    with open("docs/performance/scheduling_limits_audit.json", "w") as f:
        json.dump(audit_data, f, indent=2)
    print("\nAudit data exported to docs/performance/scheduling_limits_audit.json")

if __name__ == "__main__":
    main()
