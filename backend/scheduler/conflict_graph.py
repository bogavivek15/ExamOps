"""
ExamOps Scheduling Engine — Conflict Graph & Examination Prioritization
Builds student conflict graph and produces deterministic Most-Constrained-First ordering.
"""
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from backend.scheduler.models import ExamModel

class ConflictGraph:
    def __init__(self, exams: List[ExamModel]):
        self.exams = exams
        self.exam_by_id: Dict[str, ExamModel] = {e.id: e for e in exams}
        # Inverted index: student_id -> set of exam_ids
        self.student_exam_map: Dict[str, Set[str]] = defaultdict(set)
        # Adjacency matrix: exam_id -> set of conflicting exam_ids
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        # Edge weights: (exam_id_1, exam_id_2) -> count of shared students
        self.edge_weights: Dict[Tuple[str, str], int] = defaultdict(int)
        # Conflict degrees: exam_id -> total shared student conflicts
        self.conflict_degrees: Dict[str, int] = defaultdict(int)

        self._build_graph()

    def _build_graph(self):
        # 1. Map students to exams
        for ex in self.exams:
            for p in ex.participants:
                self.student_exam_map[p.student_id].add(ex.id)

        # 2. Build edges from co-enrolled students
        for student_id, exam_set in self.student_exam_map.items():
            exam_list = list(exam_set)
            for i in range(len(exam_list)):
                for j in range(i + 1, len(exam_list)):
                    e1, e2 = exam_list[i], exam_list[j]
                    self.adjacency[e1].add(e2)
                    self.adjacency[e2].add(e1)
                    pair = (min(e1, e2), max(e1, e2))
                    self.edge_weights[pair] += 1

        # 3. Calculate conflict degrees
        for (e1, e2), weight in self.edge_weights.items():
            self.conflict_degrees[e1] += weight
            self.conflict_degrees[e2] += weight

    def get_conflict_degree(self, exam_id: str) -> int:
        return self.conflict_degrees.get(exam_id, 0)

    def get_conflicting_exams(self, exam_id: str) -> Set[str]:
        return self.adjacency.get(exam_id, set())

    def get_shared_student_count(self, exam_id_1: str, exam_id_2: str) -> int:
        pair = (min(exam_id_1, exam_id_2), max(exam_id_1, exam_id_2))
        return self.edge_weights.get(pair, 0)

    def prioritize_exams(self) -> List[ExamModel]:
        """
        Sorts examinations in deterministic Most-Constrained-First order:
        1. Conflict degree (descending)
        2. Student cohort size (descending)
        3. Examination duration (descending)
        4. Institutional priority (descending)
        5. Canonical exam code (ascending tie-breaker)
        """
        return sorted(
            self.exams,
            key=lambda e: (
                -self.conflict_degrees.get(e.id, 0),
                -len(e.participants),
                -e.duration_minutes,
                -e.priority,
                e.exam_code,
            )
        )
