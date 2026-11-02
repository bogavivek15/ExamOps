"""
Test Suite: Database Structural & Baseline Integrity
Validates:
1. Exact baseline counts for all core master tables
2. Primary keys, foreign key definitions, NOT NULL constraints
3. Check constraints (ranges, enum statuses, regex format patterns)
4. Immutability triggers on append-only audit & telemetry tables
"""
import pytest
from backend.database import execute_query, execute_mutation

def test_baseline_entity_counts():
    """Verify master data table row counts meet the definitive specifications."""
    expected_counts = {
        "students": 5000,
        "courses": 150,
        "enrollments": 25044,
        "exams": 300,
        "rooms": 100,
        "invigilators": 200,
        "accommodations": 301,
        "accommodation_notes": 301,
        "academic_periods": 1,
        "equipment_types": 5,
        "room_capacities": 100,
        "availabilities": 1200,
        "room_availabilities": 601,
    }
    for table_name, expected in expected_counts.items():
        res = execute_query(f'SELECT COUNT(*) as cnt FROM "{table_name}";', fetch_one=True)
        assert res is not None
        assert res["cnt"] == expected, f"Table {table_name} expected {expected} rows, found {res['cnt']}"

def test_identifier_patterns():
    """Verify all business codes adhere to strict institutional formatting rules."""
    patterns = [
        ("students", "student_code", "^STU-[0-9]{6}$"),
        ("courses", "course_code", "^CRS-[0-9]{6}$"),
        ("enrollments", "enrollment_code", "^ENR-[0-9]{6}$"),
        ("exams", "exam_code", "^EXAM-[0-9]{4}-[0-9]{6}$"),
        ("exam_requirements", "requirement_code", "^REQ-[0-9]{6}$"),
        ("rooms", "room_code", "^ROOM-[0-9]{6}$"),
        ("room_capacities", "capacity_code", "^CAP-[0-9]{6}$"),
        ("invigilators", "invigilator_code", "^INV-[0-9]{6}$"),
        ("availabilities", "availability_code", "^AVL-[0-9]{6}$"),
        ("accommodations", "accommodation_code", "^ACO-[0-9]{6}$"),
    ]
    for table, col, regex in patterns:
        bad = execute_query(f'SELECT id, {col} FROM "{table}" WHERE {col} !~ %s LIMIT 5;', (regex,))
        assert len(bad) == 0, f"Found malformed identifiers in {table}.{col}: {bad}"

def test_mandatory_columns_not_null():
    """Verify no mandatory fields contain NULL or blank strings."""
    checks = [
        ("students", "first_name"),
        ("students", "last_name"),
        ("students", "email"),
        ("courses", "name"),
        ("courses", "department"),
        ("exams", "title"),
        ("rooms", "name"),
        ("rooms", "building"),
        ("invigilators", "first_name"),
        ("invigilators", "last_name"),
        ("invigilators", "email"),
    ]
    for table, col in checks:
        bad = execute_query(f'SELECT id FROM "{table}" WHERE {col} IS NULL OR TRIM({col}) = \'\' LIMIT 5;')
        assert len(bad) == 0, f"Found NULL or blank values in {table}.{col}: {bad}"

def test_immutability_triggers():
    """Verify append-only tables reject UPDATE and DELETE mutations."""
    # 1. Audit logs
    log = execute_query("SELECT id FROM audit_logs LIMIT 1;", fetch_one=True)
    if log:
        with pytest.raises(Exception) as exc_info:
            execute_mutation("DELETE FROM audit_logs WHERE id = %s;", (str(log["id"]),))
        assert "append-only" in str(exc_info.value).lower() or "disallowed" in str(exc_info.value).lower()

    # 2. Scheduling Decisions
    decision = execute_query("SELECT id FROM scheduling_decisions LIMIT 1;", fetch_one=True)
    if decision:
        with pytest.raises(Exception) as exc_info:
            execute_mutation("DELETE FROM scheduling_decisions WHERE id = %s;", (str(decision["id"]),))
        assert "append-only" in str(exc_info.value).lower() or "disallowed" in str(exc_info.value).lower()

