import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import execute_query

def analyze_graph():
    # Fetch all enrollments
    enrollments = execute_query("""
        SELECT enr.student_id, ex.id as exam_id, ex.exam_code
        FROM enrollments enr
        JOIN exams ex ON ex.course_id = enr.course_id
        WHERE enr.academic_period_id = '11111111-1111-1111-1111-111111111111';
    """)
    from collections import defaultdict
    student_exams = defaultdict(set)
    exam_students = defaultdict(set)
    for r in enrollments:
        student_exams[r['student_id']].add(r['exam_id'])
        exam_students[r['exam_id']].add(r['student_id'])

    adjacency = defaultdict(set)
    for s_id, ex_set in student_exams.items():
        ex_list = list(ex_set)
        for i in range(len(ex_list)):
            for j in range(i+1, len(ex_list)):
                adjacency[ex_list[i]].add(ex_list[j])
                adjacency[ex_list[j]].add(ex_list[i])

    total_exams = len(exam_students)
    total_edges = sum(len(adj) for adj in adjacency.values()) // 2
    max_possible_edges = (total_exams * (total_exams - 1)) // 2
    density = total_edges / max_possible_edges if max_possible_edges > 0 else 0

    degrees = [len(adj) for adj in adjacency.values()]
    print(f"Total Exams in Graph: {total_exams}")
    print(f"Total Conflict Edges: {total_edges} / {max_possible_edges} (Graph Density: {density:.3f})")
    print(f"Min Conflict Degree: {min(degrees)}, Max Conflict Degree: {max(degrees)}, Avg Conflict Degree: {sum(degrees)/len(degrees):.1f}")

    # Maximum Clique / Degree estimation
    # If average exam conflicts with ~200 other exams out of 300!
    # And invigilator workload cap: 200 invigilators, max hours per day/week!

if __name__ == '__main__':
    analyze_graph()

