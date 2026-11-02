# ExamOps — Synthetic Dataset Source Manifest & Provenance Specification

**Specification Version:** 1.0.0  
**Last Updated:** 2026-11-03  
**Compliance Authority:** YottaFlex AI Problem Statement §12 ("Public Data Guidance / Lawful Use") & Candidate FAQ Q12  

---

## 1. Dataset Origin & Lawful Provenance Statement

- **100% Deterministic Synthetic Data:** All student records, course names, enrollments, examination requirements, room dimensions, invigilator profiles, availability blocks, and student accommodations in this repository were deterministically generated using the standalone Python generator located in [`generator/`](../generator/).
- **Zero Confidential / Real PII:** No actual human personal data, student records, academic transcripts, or institutional credentials were collected, imported, or utilized.
  - All email addresses use the synthetic institutional domain `@student.institution.edu` or `@staff.institution.edu`.
  - All names and attributes were synthesized using pseudo-random distributions initialized from a fixed seed.
- **Lawful Provenance:** No external copyrighted datasets, scraping routines, or unauthorized proprietary schemas were employed. The data schema was designed from scratch to satisfy the relational requirements of the problem statement.

---

## 2. Generator Configuration & Profiles

| Property | Value | Description |
|---|---|---|
| **Generator Location** | [`generator/generate.py`](../generator/generate.py) | Standalone deterministic generation engine |
| **Configuration Module** | [`generator/config.py`](../generator/config.py) | Pydantic / Dataclass generation parameters |
| **Exporters Module** | [`generator/exporters.py`](../generator/exporters.py) | CSV, JSON, and bulk SQL format serializes |
| **Negative Scenarios Module** | [`generator/negative_scenarios.py`](../generator/negative_scenarios.py) | Injects 5 mandatory negative anomaly cases |
| **Generator Version** | `1.0.0` | Production baseline generator |
| **Master Deterministic Seed** | `20261022` | Fixed seed ensuring byte-reproducible generation |

### Generator Profiles

1. **Starter Profile (`STARTER_PROFILE`):**
   - Students: 500
   - Exams: 30
   - Rooms: 10
   - Invigilators: 20
   - Used for quick local testing and fast CI iterations.

2. **Full Baseline Profile (`FULL_PROFILE`):**
   - Students: 5,000
   - Exams: 300
   - Rooms: 100
   - Invigilators: 200
   - Authoritative benchmark volume satisfying Problem Statement §4.

---

## 3. Dataset Entity Counts (Full Profile)

| Entity | Primary Key Pattern | Row Count | Target Output CSV | Target Output JSON |
|---|---|---|---|---|
| **AcademicPeriod** | `uuid` | 1 | `data/csv/academic_periods.csv` | `data/json/academic_periods.json` |
| **Student** | `STU-NNNNNN` | 5,000 | `data/csv/students.csv` | `data/json/students.json` |
| **Course** | `CRS-NNNNNN` | 150 | `data/csv/courses.csv` | `data/json/courses.json` |
| **Enrollment** | `ENR-NNNNNN` | 25,044 | `data/csv/enrollments.csv` | `data/json/enrollments.json` |
| **Exam** | `EXAM-2026-NNNNNN` | 300 | `data/csv/exams.csv` | `data/json/exams.json` |
| **ExamRequirement** | `REQ-NNNNNN` | 107 | `data/csv/exam_requirements.csv` | `data/json/exam_requirements.json` |
| **Room** | `ROOM-NNNNNN` | 100 | `data/csv/rooms.csv` | `data/json/rooms.json` |
| **RoomCapacity** | `CAP-NNNNNN` | 100 | `data/csv/room_capacities.csv` | `data/json/room_capacities.json` |
| **RoomAvailability**| `AVL-NNNNNN` | 601 | `data/csv/room_availabilities.csv`| `data/json/room_availabilities.json`|
| **RoomEquipment** | `REQ-NNNNNN` | 136 | `data/csv/room_equipment.csv` | `data/json/room_equipment.json` |
| **EquipmentType** | `EQP-NNNNNN` | 5 | `data/csv/equipment_types.csv` | `data/json/equipment_types.json` |
| **Invigilator** | `INV-NNNNNN` | 200 | `data/csv/invigilators.csv` | `data/json/invigilators.json` |
| **Availability** | `AVL-NNNNNN` | 1,200 | `data/csv/availabilities.csv` | `data/json/availabilities.json` |
| **Accommodation** | `ACO-NNNNNN` | 301 | `data/csv/accommodations.csv` | `data/json/accommodations.json` |
| **AccommodationNote**| `NOT-NNNNNN` | 301 | `data/csv/accommodation_notes.csv`| `data/json/accommodation_notes.json`|
| **CourseInstructor**| `INS-NNNNNN` | 150 | `data/csv/course_instructors.csv` | `data/json/course_instructors.json` |
| **UserProfile** | `USR-NNNNNN` | 45 | `data/csv/user_profiles.csv` | `data/json/user_profiles.json` |

---

## 4. Output Formats & Ground Truth Isolation

- **CSV Datasets:** Located in [`data/csv/`](../data/csv/) (17 tabular files).
- **JSON Datasets:** Located in [`data/json/`](../data/json/) (17 structured JSON files).
- **SQL Seed Script:** Located at [`data/sql/seed_data.sql`](../data/sql/seed_data.sql) (6.2 MB bulk insertion script compatible with PostgreSQL 15/16 and Supabase).
- **Ground Truth Isolation:**
  - Anomaly edge cases are isolated in [`data/ground_truth.csv`](../data/ground_truth.csv) and [`data/ground_truth.json`](../data/ground_truth.json).
  - Ground truth labels (`expected_constraint_violated`, `expected_reason_code`, `expected_outcome`) are strictly excluded from input training/operational features, completely preventing pipeline data leakage.
- **SHA-256 Checksum Manifest:**
  - Located at [`data/manifest.json`](../data/manifest.json).
  - Contains cryptographic SHA-256 digests for all generated CSV, JSON, and SQL files.

---

## 5. Two-Run Reproducibility Verification

Reproducibility is verified using the dedicated dataset validation suite:

```bash
python scripts/test_synthetic_data.py
```

This verification:
1. Executes `generator/generate.py` twice with fixed seed `20261022` in isolated directories.
2. Compares line counts and SHA-256 cryptographic digests across both generation outputs.
3. Asserts 100% hash parity, proving the dataset generation is fully deterministic and reproducible.
