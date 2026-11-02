"""
ExamOps Automated Distributed Concurrency Safety Tests
Validates PostgreSQL-backed distributed advisory locks under concurrent executions,
multi-worker / multi-process emulation, crash resilience, and cross-run isolation.
"""
import pytest
import time
import uuid
import threading
import subprocess
import sys
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import execute_query, execute_mutation, get_db_cursor
from backend.services.distributed_lock import (
    distributed_advisory_lock,
    DistributedLockConflictError,
    hash_to_postgres_bigint,
)

client = TestClient(app)

@pytest.fixture(scope="module")
def admin_user():
    prof = execute_query(
        "SELECT id, email, role FROM user_profiles WHERE role = 'ACADEMIC_ADMINISTRATOR' AND status = 'ACTIVE' LIMIT 1;",
        fetch_one=True,
    )
    assert prof is not None
    return prof

@pytest.fixture(scope="module")
def test_period():
    p = execute_query(
        "SELECT id, name FROM academic_periods WHERE is_active = TRUE LIMIT 1;",
        fetch_one=True,
    )
    assert p is not None
    return p

def test_distributed_advisory_lock_mutual_exclusion():
    """Verifies that two threads or processes cannot hold the same advisory lock simultaneously."""
    res_key = f"test-run-{uuid.uuid4()}"
    results = []

    def attempt_lock(thread_id):
        try:
            with distributed_advisory_lock(res_key) as lock_id:
                results.append((thread_id, "ACQUIRED", lock_id))
                time.sleep(1.0)
        except DistributedLockConflictError:
            results.append((thread_id, "CONFLICT", None))

    t1 = threading.Thread(target=attempt_lock, args=(1,))
    t2 = threading.Thread(target=attempt_lock, args=(2,))

    t1.start()
    time.sleep(0.15)
    t2.start()

    t1.join()
    t2.join()

    statuses = [r[1] for r in results]
    assert "ACQUIRED" in statuses
    assert "CONFLICT" in statuses
    assert len(results) == 2

    # After t1 releases, resource should be freely acquirable again
    with distributed_advisory_lock(res_key) as lock_id:
        assert lock_id is not None

def test_different_runs_do_not_block_each_other():
    """Verifies that distinct runs have distinct lock keys and do not block one another."""
    res_key_1 = f"test-run-A-{uuid.uuid4()}"
    res_key_2 = f"test-run-B-{uuid.uuid4()}"

    acquired = []

    def run_worker(k):
        with distributed_advisory_lock(k) as l_id:
            acquired.append((k, l_id))
            time.sleep(0.5)

    t1 = threading.Thread(target=run_worker, args=(res_key_1,))
    t2 = threading.Thread(target=run_worker, args=(res_key_2,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    assert len(acquired) == 2
    assert acquired[0][0] != acquired[1][0]
    assert acquired[0][1] != acquired[1][1]

def test_multi_process_advisory_lock_isolation():
    """
    Spawns two truly independent operating system processes to prove cross-process
    mutual exclusion (the exact architecture of multi-worker Uvicorn on Render).
    """
    run_id = f"proc-test-{uuid.uuid4()}"

    worker_code = f"""
import sys, time
from backend.services.distributed_lock import distributed_advisory_lock, DistributedLockConflictError

action = sys.argv[1]
if action == "hold":
    with distributed_advisory_lock("{run_id}"):
        print("HELD", flush=True)
        time.sleep(2.0)
elif action == "try":
    time.sleep(0.4)
    try:
        with distributed_advisory_lock("{run_id}"):
            print("UNEXPECTED_ACQUIRE", flush=True)
    except DistributedLockConflictError:
        print("CONFLICT_REJECTED", flush=True)
"""

    p1 = subprocess.Popen([sys.executable, "-c", worker_code, "hold"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p2 = subprocess.Popen([sys.executable, "-c", worker_code, "try"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    out1, _ = p1.communicate(timeout=10)
    out2, _ = p2.communicate(timeout=10)

    assert "HELD" in out1
    assert "CONFLICT_REJECTED" in out2

def test_worker_crash_releases_advisory_lock():
    """
    Verifies that if a backend worker process abruptly crashes (SIGTERM/kill),
    PostgreSQL session cleanup automatically releases the lock immediately.
    """
    crash_key = f"crash-test-{uuid.uuid4()}"

    crash_code = f"""
import time
from backend.services.distributed_lock import distributed_advisory_lock
with distributed_advisory_lock("{crash_key}"):
    print("LOCK_HELD", flush=True)
    time.sleep(30.0)
"""

    p = subprocess.Popen([sys.executable, "-c", crash_code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(1.0)
    p.terminate()
    p.wait(timeout=5)

    # Immediately attempt acquisition in parent process
    with distributed_advisory_lock(crash_key) as l_id:
        assert l_id is not None

def test_scheduling_routes_return_409_on_concurrent_execution(admin_user, test_period):
    """
    Tests that simultaneous API execution requests to /scheduling/runs/{id}/execute
    return HTTP 409 Conflict for the second caller instead of executing concurrently.
    """
    headers = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}

    # 1. Create a draft run
    create_res = client.post(
        "/api/scheduling/runs",
        json={"academic_period_id": test_period["id"], "algorithm_version": "1.0.0", "seed": 20261022},
        headers=headers,
    )
    assert create_res.status_code == 200
    run_id = create_res.json()["id"]

    try:
        # 2. Acquire the advisory lock on that run to simulate worker 1 actively executing
        with distributed_advisory_lock(run_id):
            # 3. Simulate worker 2 receiving an execute request for the same run
            concurrent_res = client.post(f"/api/scheduling/runs/{run_id}/execute", headers=headers)
            assert concurrent_res.status_code == 409
            err_detail = concurrent_res.json().get("detail", "")
            assert "already actively executing" in err_detail
    finally:
        # Cleanup test run
        execute_mutation("DELETE FROM scheduling_runs WHERE id = %s;", (run_id,))

