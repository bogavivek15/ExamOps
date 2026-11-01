"""
ExamOps Deterministic Scheduling Engine
Most-Constrained-First Greedy Algorithm with Bounded Improvement Passes.
Guarantees zero hard-constraint violations in confirmed assignments and explainable decision telemetry.
"""
from datetime import datetime, date, time, timedelta, timezone
from typing import List, Dict, Any, Tuple, Optional, Set
from collections import defaultdict
import math

from backend.scheduler.models import (
    ExamModel,
    RoomModel,
    InvigilatorModel,
    ExamParticipant,
    CandidateSlot,
    RoomAllocation,
    CandidateAssignment,
    DecisionRecord,
)
from backend.scheduler.conflict_graph import ConflictGraph
from backend.scheduler.candidate_generator import CandidateSlotGenerator
from backend.scheduler.constraints import ConstraintChecker
from backend.scheduler.room_allocator import RoomAllocator
from backend.scheduler.invigilator_allocator import InvigilatorAllocator
from backend.scheduler.scoring import compute_candidate_score
from backend.scheduler.schedule_validator import ScheduleValidator

class SchedulingEngine:
    def __init__(
        self,
        exams: List[ExamModel],
        rooms: List[RoomModel],
        invigilators: List[InvigilatorModel],
        start_date: date,
        end_date: date,
        daily_start_time: time = time(8, 0),
        daily_end_time: time = time(18, 0),
        slot_granularity_minutes: int = 30,
        max_improvement_passes: int = 3,
    ):
        self.exams = exams
        self.rooms = rooms
        self.invigilators = invigilators
        self.start_date = start_date
        self.end_date = end_date
        self.max_improvement_passes = max_improvement_passes

        self.slot_generator = CandidateSlotGenerator(
            start_date=start_date,
            end_date=end_date,
            daily_start_time=daily_start_time,
            daily_end_time=daily_end_time,
            slot_granularity_minutes=slot_granularity_minutes,
            skip_sundays=True,
        )
        self.room_allocator = RoomAllocator(rooms)
        self.invigilator_allocator = InvigilatorAllocator(invigilators)

        # Committed Calendars and State
        # student_id -> list of (start_dt, end_dt, exam_code)
        self.student_calendar: Dict[str, List[Tuple[datetime, datetime, str]]] = defaultdict(list)
        # room_id -> list of (start_dt, end_dt, exam_code)
        self.room_calendar: Dict[str, List[Tuple[datetime, datetime, str]]] = defaultdict(list)
        # invigilator_id -> list of (start_dt, end_dt, room_code)
        self.invigilator_calendar: Dict[str, List[Tuple[datetime, datetime, str]]] = defaultdict(list)
        # Workload tracking
        self.invigilator_daily_hours: Dict[Tuple[str, date], float] = defaultdict(float)
        self.invigilator_weekly_hours: Dict[Tuple[str, int], float] = defaultdict(float)

        # Output collections
        self.confirmed_assignments: List[Dict[str, Any]] = []
        self.student_seatings: List[Dict[str, Any]] = []
        self.invigilator_staffings: List[Dict[str, Any]] = []
        self.decisions: List[DecisionRecord] = []
        self.unassigned_exams: List[Dict[str, Any]] = []

    def execute_schedule(self) -> Dict[str, Any]:
        """
        Executes the full examination scheduling procedure.
        """
        # Step 1: Build conflict graph and prioritize exams
        conflict_graph = ConflictGraph(self.exams)
        prioritized_exams = conflict_graph.prioritize_exams()

        unassigned_queue: List[ExamModel] = []
        decision_order = 1

        # Step 2: Pass 1 — Most-Constrained-First Greedy Placement
        for exam in prioritized_exams:
            success = self._evaluate_and_place_exam(exam, decision_order)
            if not success:
                unassigned_queue.append(exam)
            decision_order += 1

        # Step 3: Passes 2 to N — Bounded Improvement Passes
        for pass_num in range(2, self.max_improvement_passes + 1):
            if not unassigned_queue:
                break
            remaining_unassigned: List[ExamModel] = []
            for exam in unassigned_queue:
                success = self._evaluate_and_place_exam(exam, decision_order, pass_number=pass_num)
                if not success:
                    remaining_unassigned.append(exam)
                decision_order += 1
            unassigned_queue = remaining_unassigned

        # Step 4: Record unassigned summary
        for exam in unassigned_queue:
            latest_decision = next((d for d in reversed(self.decisions) if d.exam_id == exam.id), None)
            reason_codes = latest_decision.reason_codes if latest_decision else ["UNKNOWN_CONSTRAINT"]
            self.unassigned_exams.append({
                "exam_id": exam.id,
                "exam_code": exam.exam_code,
                "title": exam.title,
                "cohort_size": len(exam.participants),
                "duration_minutes": exam.duration_minutes,
                "reason_codes": reason_codes,
            })

        # Step 5: Independent Schedule Validation
        validator = ScheduleValidator(self.exams, self.rooms, self.invigilators)
        is_certified, violations = validator.validate_confirmed_schedule(
            assignments=self.confirmed_assignments,
            student_seatings=self.student_seatings,
            invigilator_staffings=self.invigilator_staffings,
        )

        # Step 6: Compute operational metrics
        total_exams = len(self.exams)
        scheduled_count = len(self.exams) - len(self.unassigned_exams)
        unassigned_count = len(self.unassigned_exams)
        completion_pct = round((scheduled_count / total_exams) * 100.0, 2) if total_exams > 0 else 0.0

        total_students_enrolled = sum(len(e.participants) for e in self.exams)
        students_scheduled = len(self.student_seatings)
        student_coverage_pct = round((students_scheduled / total_students_enrolled) * 100.0, 2) if total_students_enrolled > 0 else 0.0

        return {
            "status": "COMPLETED",
            "is_certified_valid": is_certified,
            "violations_count": len(violations),
            "violations": violations,
            "metrics": {
                "total_exams": total_exams,
                "scheduled_count": scheduled_count,
                "unassigned_count": unassigned_count,
                "completion_percentage": completion_pct,
                "total_student_exam_registrations": total_students_enrolled,
                "scheduled_student_exam_registrations": students_scheduled,
                "student_coverage_percentage": student_coverage_pct,
                "confirmed_room_assignments_count": len(self.confirmed_assignments),
                "invigilator_staffings_count": len(self.invigilator_staffings),
            },
            "assignments": self.confirmed_assignments,
            "student_seatings": self.student_seatings,
            "invigilator_staffings": self.invigilator_staffings,
            "decisions": [
                {
                    "exam_id": d.exam_id,
                    "exam_code": d.exam_code,
                    "decision_order": d.decision_order,
                    "is_assigned": d.is_assigned,
                    "reason_codes": d.reason_codes,
                    "selected_candidate": d.selected_candidate,
                    "candidate_details": d.candidate_details,
                }
                for d in self.decisions
            ],
            "unassigned_exams": self.unassigned_exams,
        }

    def _evaluate_and_place_exam(
        self,
        exam: ExamModel,
        decision_order: int,
        pass_number: int = 1,
    ) -> bool:
        """
        Generates and evaluates candidate slots for an examination.
        Selects best-scoring candidate or logs failure telemetry.
        """
        max_student_duration = max(
            [p.effective_duration_minutes for p in exam.participants],
            default=exam.duration_minutes
        )
        slots = self.slot_generator.generate_slots(max_student_duration)

        valid_candidates: List[CandidateAssignment] = []
        rejected_reasons: Set[str] = set()
        evaluated_slot_count = 0

        for slot in slots:
            evaluated_slot_count += 1

            # 1. Check Student Non-Overlap
            student_chk = ConstraintChecker.check_student_non_overlap(
                exam.participants, slot.start_dt, slot.end_dt, self.student_calendar
            )
            if not student_chk.is_valid:
                rejected_reasons.update(student_chk.reason_codes)
                continue

            # 2. Allocate Rooms (implements 7 room-splitting invariants)
            allocations, room_reasons = self.room_allocator.allocate_rooms(
                exam, slot, self.room_calendar
            )
            if not allocations:
                rejected_reasons.update(room_reasons)
                continue

            # 3. Check Room Accommodations (accessibility, quiet venue)
            acc_passed = True
            for alloc in allocations:
                acc_chk = ConstraintChecker.check_room_accommodation(alloc.room, alloc.seated_students)
                if not acc_chk.is_valid:
                    rejected_reasons.update(acc_chk.reason_codes)
                    acc_passed = False
                    break
            if not acc_passed:
                continue

            # 4. Allocate Invigilators
            inv_success, inv_reasons = self.invigilator_allocator.allocate_invigilators(
                allocations,
                self.invigilator_calendar,
                self.invigilator_daily_hours,
                self.invigilator_weekly_hours,
            )
            if not inv_success:
                rejected_reasons.update(inv_reasons)
                continue

            # 5. Candidate is valid! Compute multi-objective score
            score = compute_candidate_score(allocations, slot.slot_index)
            candidate = CandidateAssignment(
                exam=exam,
                slot=slot,
                allocations=allocations,
                score=score,
            )
            valid_candidates.append(candidate)

            # In greedy heuristic, stop early if a high-quality single-room candidate is discovered
            if score[0] == 1 and score[1] <= 10:
                break

        if not valid_candidates:
            # Record negative decision telemetry
            reason_list = sorted(list(rejected_reasons)) if rejected_reasons else ["NO_FEASIBLE_CANDIDATE"]
            self.decisions.append(DecisionRecord(
                exam_id=exam.id,
                exam_code=exam.exam_code,
                decision_order=decision_order,
                is_assigned=False,
                reason_codes=reason_list,
                selected_candidate=None,
                candidate_details={
                    "evaluated_slots": evaluated_slot_count,
                    "pass_number": pass_number,
                    "cohort_size": len(exam.participants),
                },
            ))
            return False

        # Select candidate with minimal penalty score
        best_candidate = min(valid_candidates, key=lambda c: c.score)

        # Commit assignments to calendar states
        self._commit_assignment(best_candidate)

        # Record positive decision telemetry
        selected_info = {
            "start_time": best_candidate.slot.start_dt.isoformat(),
            "end_time": best_candidate.slot.end_dt.isoformat(),
            "date": best_candidate.slot.date_val.isoformat(),
            "num_rooms": len(best_candidate.allocations),
            "room_codes": [a.room.room_code for a in best_candidate.allocations],
            "total_seated": sum(len(a.seated_students) for a in best_candidate.allocations),
            "score": list(best_candidate.score),
        }
        self.decisions.append(DecisionRecord(
            exam_id=exam.id,
            exam_code=exam.exam_code,
            decision_order=decision_order,
            is_assigned=True,
            reason_codes=[],
            selected_candidate=selected_info,
            candidate_details={
                "evaluated_slots": evaluated_slot_count,
                "valid_slots_found": len(valid_candidates),
                "pass_number": pass_number,
            },
        ))
        return True

    def _commit_assignment(self, candidate: CandidateAssignment):
        """
        Commits chosen room and invigilator allocations to active calendars and outputs.
        """
        exam = candidate.exam
        slot = candidate.slot

        for alloc in candidate.allocations:
            room = alloc.room
            room_start = alloc.room_start_dt
            room_end = alloc.room_end_dt
            assignment_code = f"ASN-{exam.exam_code}-{room.room_code}"
            assignment_id = f"asn-{exam.id[:8]}-{room.id[:8]}"

            # 1. Record ScheduleAssignment
            self.confirmed_assignments.append({
                "id": assignment_id,
                "assignment_code": assignment_code,
                "exam_id": exam.id,
                "exam_code": exam.exam_code,
                "room_id": room.id,
                "room_code": room.room_code,
                "start_time": room_start.isoformat(),
                "end_time": room_end.isoformat(),
                "status": "CONFIRMED",
            })

            # Update room calendar
            self.room_calendar[room.id].append((room_start, room_end, exam.exam_code))

            # 2. Record AssignmentStudent seatings
            for p in alloc.seated_students:
                p_end = room_start + timedelta(minutes=p.effective_duration_minutes)
                self.student_seatings.append({
                    "id": f"as-{assignment_id[:8]}-{p.student_id[:8]}",
                    "assignment_id": assignment_id,
                    "exam_id": exam.id,
                    "student_id": p.student_id,
                    "student_code": p.student_code,
                    "room_id": room.id,
                    "effective_duration_minutes": p.effective_duration_minutes,
                    "start_time": room_start.isoformat(),
                    "end_time": p_end.isoformat(),
                    "requires_accessible_room": p.requires_accessible_room,
                })
                # Update student calendar
                self.student_calendar[p.student_id].append((room_start, p_end, exam.exam_code))

            # 3. Record AssignmentInvigilator staffings
            for inv in alloc.assigned_invigilators:
                self.invigilator_staffings.append({
                    "id": f"ai-{assignment_id[:8]}-{inv.id[:8]}",
                    "assignment_id": assignment_id,
                    "invigilator_id": inv.id,
                    "invigilator_code": inv.invigilator_code,
                    "role": "PRIMARY",
                    "start_time": room_start.isoformat(),
                    "end_time": room_end.isoformat(),
                })
                # Update invigilator calendar & workload
                self.invigilator_calendar[inv.id].append((room_start, room_end, room.room_code))
                dur_hrs = (room_end - room_start).total_seconds() / 3600.0
                shift_d = room_start.date()
                week_n = shift_d.isocalendar()[1]
                self.invigilator_daily_hours[(inv.id, shift_d)] += dur_hrs
                self.invigilator_weekly_hours[(inv.id, week_n)] += dur_hrs

