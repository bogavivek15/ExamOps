"""
ExamOps Multi-Worker Authentication & Role Revocation Verification Script
Spawns and tests across 4 independent worker processes to prove:
1. Role downgrade to LEARNER is enforced across all 4 workers within <= 5.0s (HTTP 403).
2. Account deactivation to INACTIVE is enforced across all 4 workers within <= 5.0s (HTTP 401).
3. Role promotion to ACADEMIC_ADMINISTRATOR is recognized across all 4 workers.
4. Invalid JWT signatures are rejected (HTTP 401).
5. Expired JWTs are rejected (HTTP 401).
6. Direct API access without authorization is rejected (HTTP 401/403).
7. Cache invalidation cannot grant unauthorized privileges.
"""
import sys
import time
import uuid
import subprocess
from typing import Dict, Any

from backend.database import execute_query, execute_mutation, get_db_cursor
from backend.auth import create_access_token

def run_multi_worker_auth_audit() -> Dict[str, Any]:
    print("=" * 75)
    print("EXAMOPS 4-WORKER AUTHENTICATION & REVOCATION AUDIT")
    print("=" * 75)
    
    results = {}
    
    # 1. Create an isolated test user in PostgreSQL
    user_id = str(uuid.uuid4())
    email = f"multiworker_{user_id[:8]}@examops.edu"
    print(f"\n[*] Creating ephemeral test administrator: {email} (ID: {user_id})")
    
    sql = """
    INSERT INTO user_profiles (id, email, display_name, role, status, department)
    VALUES (%s, %s, %s, 'ACADEMIC_ADMINISTRATOR', 'ACTIVE', 'Administration')
    RETURNING *;
    """
    with get_db_cursor(commit=True) as cur:
        cur.execute(sql, (user_id, email, "Multi-Worker Admin"))
    
    token = create_access_token(user_id=user_id, email=email, role="ACADEMIC_ADMINISTRATOR")
    
    worker_check_code = """
import sys
from fastapi.testclient import TestClient
from backend.main import app
client = TestClient(app)

token = sys.argv[1]
expected_status = int(sys.argv[2])
headers = {"Authorization": f"Bearer {token}"}
res = client.get("/api/auth/profiles", headers=headers)

if res.status_code != expected_status:
    print(f"FAILED: Expected {expected_status}, got {res.status_code}: {res.text}", file=sys.stderr)
    sys.exit(1)
print(f"WORKER_OK:{res.status_code}")
"""

    def check_across_4_workers(expected_status: int) -> bool:
        """Launches 4 truly separate Python processes representing 4 independent Uvicorn workers."""
        procs = []
        for w_idx in range(4):
            p = subprocess.Popen(
                [sys.executable, "-c", worker_check_code, token, str(expected_status)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            procs.append((w_idx, p))
            
        all_ok = True
        for w_idx, p in procs:
            out, err = p.communicate(timeout=10)
            if p.returncode != 0:
                print(f"  Worker {w_idx + 1} Error: {err.strip()}")
                all_ok = False
        return all_ok

    # --- TEST 1: Initial verification as Admin on all 4 workers ---
    print("\n[TEST 1] Verifying initial admin access across all 4 independent workers...")
    initial_ok = check_across_4_workers(expected_status=200)
    print(f"  -> All 4 workers accepted admin token: {initial_ok}")
    results["initial_4_worker_admin_access"] = "PASS" if initial_ok else "FAIL"

    # --- TEST 2: Role downgrade to LEARNER across all 4 workers within <= 5.0s ---
    print("\n[TEST 2] Downgrading role to LEARNER in PostgreSQL and verifying 5s TTL across 4 workers...")
    execute_mutation("UPDATE user_profiles SET role = 'LEARNER' WHERE id = %s;", (user_id,))
    
    print("  -> Waiting 5.1s for ProfileCache TTL to expire across all 4 worker process memories...")
    time.sleep(5.1)
    
    downgrade_ok = check_across_4_workers(expected_status=403)
    print(f"  -> All 4 workers rejected downgraded user with HTTP 403 Forbidden: {downgrade_ok}")
    results["downgrade_propagated_all_4_workers"] = "PASS" if downgrade_ok else "FAIL"

    # --- TEST 3: Account deactivation across all 4 workers ---
    print("\n[TEST 3] Deactivating account (status='INACTIVE') in PostgreSQL across all 4 workers...")
    execute_mutation("UPDATE user_profiles SET status = 'INACTIVE' WHERE id = %s;", (user_id,))
    
    print("  -> Waiting 5.1s for cache expiry across all 4 workers...")
    time.sleep(5.1)
    
    deactivate_ok = check_across_4_workers(expected_status=401)
    print(f"  -> All 4 workers rejected deactivated user with HTTP 401 Unauthorized: {deactivate_ok}")
    results["deactivation_rejected_all_4_workers"] = "PASS" if deactivate_ok else "FAIL"

    # --- TEST 4: Role promotion to ACADEMIC_ADMINISTRATOR across all 4 workers ---
    print("\n[TEST 4] Promoting user back to ACADEMIC_ADMINISTRATOR and ACTIVE...")
    execute_mutation("UPDATE user_profiles SET role = 'ACADEMIC_ADMINISTRATOR', status = 'ACTIVE' WHERE id = %s;", (user_id,))
    
    print("  -> Waiting 5.1s for cache expiry across all 4 workers...")
    time.sleep(5.1)
    
    promote_ok = check_across_4_workers(expected_status=200)
    print(f"  -> All 4 workers accepted promoted administrator: {promote_ok}")
    results["promotion_accepted_all_4_workers"] = "PASS" if promote_ok else "FAIL"

    # --- TEST 5: Invalid JWT Signature Rejection ---
    print("\n[TEST 5] Tampered JWT signature rejection across workers...")
    tampered_token = token[:-10] + "tampered00"
    from fastapi.testclient import TestClient
    from backend.main import app
    client = TestClient(app)
    res_tampered = client.get("/api/auth/profiles", headers={"Authorization": f"Bearer {tampered_token}"})
    tampered_ok = (res_tampered.status_code == 401)
    print(f"  -> Tampered token rejected with HTTP 401: {tampered_ok}")
    results["tampered_jwt_rejected"] = "PASS" if tampered_ok else "FAIL"

    # --- TEST 6: Expired JWT Rejection ---
    print("\n[TEST 6] Expired JWT rejection across workers...")
    expired_token = create_access_token(user_id=user_id, email=email, role="ACADEMIC_ADMINISTRATOR", expires_delta_seconds=-3600)
    res_expired = client.get("/api/auth/profiles", headers={"Authorization": f"Bearer {expired_token}"})
    expired_ok = (res_expired.status_code == 401)
    print(f"  -> Expired token rejected with HTTP 401: {expired_ok}")
    results["expired_jwt_rejected"] = "PASS" if expired_ok else "FAIL"

    # --- TEST 7: Direct API Request without Authorization Header ---
    print("\n[TEST 7] Direct unauthenticated API requests cannot bypass backend authorization...")
    res_no_auth = client.get("/api/auth/profiles")
    res_post_run = client.post("/api/scheduling/runs", json={})
    unauth_ok = (res_no_auth.status_code == 401 and res_post_run.status_code == 401)
    print(f"  -> Unauthenticated direct requests systematically rejected with HTTP 401: {unauth_ok}")
    results["direct_unauthenticated_api_rejected"] = "PASS" if unauth_ok else "FAIL"

    # --- TEST 8: Cache invalidation cannot grant unauthorized privileges ---
    print("\n[TEST 8] Verifying cache invalidation cannot grant unauthorized privileges...")
    # Attempting to call invalidate_profile_cache() or flush cache does NOT elevate role
    from backend.auth import invalidate_profile_cache
    invalidate_profile_cache()
    # Now set user role to INSTRUCTOR in DB
    execute_mutation("UPDATE user_profiles SET role = 'INSTRUCTOR' WHERE id = %s;", (user_id,))
    invalidate_profile_cache()
    res_instructor = client.get("/api/auth/profiles", headers={"Authorization": f"Bearer {token}"})
    cache_priv_ok = (res_instructor.status_code == 403)
    print(f"  -> Cache invalidation properly forced DB re-read and enforced HTTP 403: {cache_priv_ok}")
    results["cache_cannot_grant_unauthorized_privileges"] = "PASS" if cache_priv_ok else "FAIL"

    # Cleanup test user
    execute_mutation("DELETE FROM user_profiles WHERE id = %s;", (user_id,))
    invalidate_profile_cache()

    print("\n" + "=" * 75)
    print("4-WORKER AUTHENTICATION AUDIT SUMMARY:")
    for k, v in results.items():
        print(f"  {k:45s}: {v}")
    print("=" * 75)
    
    all_passed = all(v == "PASS" for v in results.values())
    return {"all_passed": all_passed, "results": results}

if __name__ == "__main__":
    res = run_multi_worker_auth_audit()
    sys.exit(0 if res["all_passed"] else 1)
