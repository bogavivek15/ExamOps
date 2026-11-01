import os
import sys
import json
from pathlib import Path
from collections import Counter

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import execute_query

def inspect_run():
    run = execute_query("SELECT id, run_code, status, scheduled_count, unassigned_count, total_exams, started_at, completed_at FROM scheduling_runs WHERE status = 'PUBLISHED' LIMIT 1;", fetch_one=True)
    if not run:
        print("No published run found!")
        return
    run_id = run['id']
    print(f"Published Run: {run['run_code']} (ID: {run_id})")
    print(f"Scheduled: {run['scheduled_count']}, Unassigned: {run['unassigned_count']}, Total: {run['total_exams']}")

    # Decision breakdowns
    decs = execute_query("""
        SELECT is_assigned, reason_codes, count(*) as cnt 
        FROM scheduling_decisions 
        WHERE scheduling_run_id = %s 
        GROUP BY is_assigned, reason_codes 
        ORDER BY is_assigned DESC, cnt DESC;
    """, (run_id,))
    print("\n--- DECISION BREAKDOWN ---")
    for d in decs:
        reasons = ", ".join(d['reason_codes']) if d['reason_codes'] else "NONE"
        status = "ASSIGNED" if d['is_assigned'] else "UNASSIGNED"
        print(f"Status: {status:<12} Reasons: {reasons:<45} Count: {d['cnt']}")

    # Sample unassigned decisions explanation
    rejected_samples = execute_query("""
        SELECT exam_id, reason_codes, selected_candidate, candidate_details
        FROM scheduling_decisions 
        WHERE scheduling_run_id = %s AND is_assigned = FALSE
        LIMIT 5;
    """, (run_id,))
    print("\n--- SAMPLE UNASSIGNED DECISION DETAILS ---")
    for r in rejected_samples:
        ex = execute_query("SELECT exam_code, title FROM exams WHERE id = %s;", (r['exam_id'],), fetch_one=True)
        code = ex['exam_code'] if ex else str(r['exam_id'])
        print(f"Exam: {code}, Reasons: {r['reason_codes']}")
        cand_details = r.get('candidate_details')
        if cand_details:
            print(f"  Candidate Details summary: {json.dumps(cand_details)[:300]}")

    # Assignment distribution per exam
    asgns = execute_query("""
        SELECT exam_id, count(*) as room_count
        FROM schedule_assignments 
        WHERE scheduling_run_id = %s 
        GROUP BY exam_id;
    """, (run_id,))
    room_counts = [a['room_count'] for a in asgns]
    print(f"\n--- ROOM ASSIGNMENT DISTRIBUTION (Scheduled Exams = {len(asgns)}) ---")
    print(f"Total Assignments (room-exam blocks): {sum(room_counts)}")
    print(f"Min rooms per exam: {min(room_counts)}, Max rooms per exam: {max(room_counts)}, Avg: {sum(room_counts)/len(room_counts):.2f}")
    
    dist = Counter(room_counts)
    for rc, cnt in sorted(dist.items()):
        print(f"  {cnt} exams required {rc} rooms")

    # Time slot distribution
    slot_dist = execute_query("""
        SELECT start_time, count(DISTINCT exam_id) as exam_cnt, count(*) as asgn_cnt
        FROM schedule_assignments
        WHERE scheduling_run_id = %s
        GROUP BY start_time
        ORDER BY start_time;
    """, (run_id,))
    print(f"\n--- TIME SLOT DISTRIBUTION ({len(slot_dist)} distinct time slots used) ---")
    for s in slot_dist[:10]:
        print(f"  Slot: {s['start_time']} -> {s['exam_cnt']} exams, {s['asgn_cnt']} room assignments")
    if len(slot_dist) > 10:
        print(f"  ... and {len(slot_dist) - 10} more slots.")

    # Room utilization
    room_util = execute_query("""
        SELECT count(DISTINCT room_id) as used_rooms FROM schedule_assignments WHERE scheduling_run_id = %s;
    """, (run_id,))
    total_rooms = execute_query("SELECT count(*) as cnt FROM rooms;", fetch_one=True)['cnt']
    print(f"\n--- RESOURCE USAGE ---")
    print(f"Rooms used: {room_util[0]['used_rooms']} / {total_rooms}")

    # Invigilator utilization
    inv_util = execute_query("""
        SELECT count(DISTINCT invigilator_id) as used_invs FROM assignment_invigilators WHERE assignment_id IN (
            SELECT id FROM schedule_assignments WHERE scheduling_run_id = %s
        );
    """, (run_id,))
    total_invs = execute_query("SELECT count(*) as cnt FROM invigilators;", fetch_one=True)['cnt']
    print(f"Invigilators used: {inv_util[0]['used_invs']} / {total_invs}")

if __name__ == '__main__':
    inspect_run()
