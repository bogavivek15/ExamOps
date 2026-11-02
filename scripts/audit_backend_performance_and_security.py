"""
ExamOps Independent Backend Performance & Security Authorization Audit
Measures repeated request latencies (p50, p95, p99), validates pagination/contracts,
and stress-tests ProfileCache against security revocation scenarios.
"""
import sys
import os
import time
import json
import uuid
from typing import Dict, Any, List
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from starlette.testclient import TestClient
from backend.main import app
from backend.database import execute_query, execute_mutation
from backend.auth import (
    create_access_token, _profile_cache, invalidate_profile_cache
)

client = TestClient(app)

def benchmark_endpoint(endpoint: str, headers: dict, iterations: int = 10) -> Dict[str, Any]:
    latencies = []
    status_codes = []
    
    # 1. Cold hit
    t0 = time.perf_counter()
    res = client.get(endpoint, headers=headers)
    t_cold = (time.perf_counter() - t0) * 1000
    latencies.append(t_cold)
    status_codes.append(res.status_code)

    # 2. Warm hits
    for _ in range(iterations - 1):
        t0 = time.perf_counter()
        res = client.get(endpoint, headers=headers)
        t_warm = (time.perf_counter() - t0) * 1000
        latencies.append(t_warm)
        status_codes.append(res.status_code)

    latencies_sorted = sorted(latencies)
    n = len(latencies_sorted)
    
    p50 = latencies_sorted[int(n * 0.50)]
    p95 = latencies_sorted[int(n * 0.95)]
    p99 = latencies_sorted[int(n * 0.99)]
    avg = sum(latencies) / n

    return {
        "endpoint": endpoint,
        "iterations": iterations,
        "cold_ms": round(t_cold, 2),
        "min_ms": round(min(latencies), 2),
        "max_ms": round(max(latencies), 2),
        "avg_ms": round(avg, 2),
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "p99_ms": round(p99, 2),
        "all_200": all(c == 200 for c in status_codes),
        "sample_response_headers": dict(res.headers),
    }

def run_backend_audit():
    print("=" * 75)
    print("EXAMOPS INDEPENDENT BACKEND BENCHMARK & SECURITY AUDIT")
    print("=" * 75)

    headers = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}

    # 1. Repeated Endpoint Latency Benchmarks
    print("\n--- 1. API Endpoint Latency Benchmarking (10 Iterations) ---")
    test_endpoints = [
        "/api/analytics/overview",
        "/api/students?limit=15",
        "/api/students?limit=15&search=Graham",
        "/api/courses?limit=15",
        "/api/exams?limit=15",
        "/api/rooms?limit=15",
        "/api/invigilators?limit=15",
        "/api/scheduling/runs?limit=10",
        "/api/audit/logs?limit=15",
    ]

    benchmark_results = []
    print(f"{'Endpoint':<35} | {'Cold (ms)':<10} | {'p50 (ms)':<10} | {'p95 (ms)':<10} | {'Status':<6}")
    print("-" * 35 + "-+-" + "-" * 10 + "-+-" + "-" * 10 + "-+-" + "-" * 10 + "-+-" + "-" * 6)

    for ep in test_endpoints:
        bm = benchmark_endpoint(ep, headers, iterations=10)
        status_str = "PASS" if bm["all_200"] else "FAIL"
        print(f"{ep:<35} | {bm['cold_ms']:10.2f} | {bm['p50_ms']:10.2f} | {bm['p95_ms']:10.2f} | {status_str:<6}")
        benchmark_results.append(bm)

    # 2. Response Model & Pagination Verification
    print("\n--- 2. Response Model & Pagination Contract Verification ---")
    res_students = client.get("/api/students?limit=15&offset=0", headers=headers)
    assert res_students.status_code == 200
    st_json = res_students.json()
    assert isinstance(st_json, list), "Students endpoint must return a list"
    assert len(st_json) <= 15, "Limit must be respected"
    has_total_header = "x-total-count" in res_students.headers
    total_count = int(res_students.headers.get("x-total-count", 0))
    print(f"  - Students Pagination: Limit 15 returned {len(st_json)} rows.")
    print(f"  - X-Total-Count Header Present: {has_total_header} (Reported Total: {total_count})")
    assert has_total_header, "x-total-count header MUST be present on paginated lists"
    assert total_count >= 5000, f"Expected total students >= 5000, got {total_count}"

    # Verify student model fields
    first_st = st_json[0]
    expected_st_fields = {"id", "student_code", "first_name", "last_name", "email", "status"}
    assert expected_st_fields.issubset(set(first_st.keys())), f"Missing expected student fields: {expected_st_fields - set(first_st.keys())}"
    print(f"  - Student Model Schema: Complete and valid ({list(first_st.keys())[:6]}...)")

    # 3. Security Vector Investigation: Profile Caching vs Revocation
    print("\n--- 3. Investigating Security Vector: ProfileCache vs Access Revocation ---")

    # Create a real temporary test user profile in database
    temp_user_id = str(uuid.uuid4())
    temp_email = f"audit_sec_test_{int(time.time())}@institution.edu"
    insert_sql = """
        INSERT INTO user_profiles (id, email, display_name, role, status)
        VALUES (%s, %s, 'Security Audit Subject', 'ACADEMIC_ADMINISTRATOR', 'ACTIVE');
    """
    execute_mutation(insert_sql, (temp_user_id, temp_email))
    print(f"  [+] Created test administrator user: {temp_email} (ID: {temp_user_id})")

    token = create_access_token(temp_user_id, temp_email, "ACADEMIC_ADMINISTRATOR")
    auth_header = {"Authorization": f"Bearer {token}"}

    # Step A: Authenticate and verify profile enters ProfileCache
    res_auth1 = client.get("/api/auth/profiles", headers=auth_header)
    assert res_auth1.status_code == 200, f"Expected 200, got {res_auth1.status_code}"
    cached_profile = _profile_cache.get(f"user:{temp_user_id}")
    assert cached_profile is not None, "ProfileCache must contain user profile"
    print(f"  [PASS] A. Profile successfully cached in memory (Role: {cached_profile.role}).")

    # Step B: Test Token Expiration Security
    # Does an expired token get accepted if user is cached in ProfileCache?
    expired_token = create_access_token(temp_user_id, temp_email, "ACADEMIC_ADMINISTRATOR", expires_delta_seconds=-300)
    res_expired = client.get("/api/auth/profiles", headers={"Authorization": f"Bearer {expired_token}"})
    assert res_expired.status_code == 401, f"Expected 401 for expired token, got {res_expired.status_code}"
    print(f"  [PASS] B. Expired token strictly rejected with HTTP 401 despite active ProfileCache entry.")

    # Step C: Test Account Deactivation Revocation Window
    # If the user is marked INACTIVE in the DB:
    execute_mutation("UPDATE user_profiles SET status = 'INACTIVE' WHERE id = %s;", (temp_user_id,))
    print("  [*] Updated user status to INACTIVE in PostgreSQL database.")

    # Check immediate access with active token and cached profile
    res_deactivated_cached = client.get("/api/auth/profiles", headers=auth_header)
    # Finding: If cached, it returns 200 until cache is invalidated!
    cache_window_active = (res_deactivated_cached.status_code == 200)
    if cache_window_active:
        print(f"  [FINDING] C. ProfileCache window observed: In-memory cache allows access for up to TTL (60s) after DB deactivation.")
    
    # Step D: Test Invalidation
    invalidate_profile_cache(f"user:{temp_user_id}")
    res_deactivated_post_invalidate = client.get("/api/auth/profiles", headers=auth_header)
    assert res_deactivated_post_invalidate.status_code in (401, 403), f"Expected 401/403 after invalidation, got {res_deactivated_post_invalidate.status_code}"
    print(f"  [PASS] D. Post-invalidation access immediately denied with HTTP {res_deactivated_post_invalidate.status_code}!")

    # Cleanup test user
    execute_mutation("DELETE FROM user_profiles WHERE id = %s;", (temp_user_id,))
    print(f"  [-] Cleaned up test user: {temp_user_id}")

    audit_summary = {
        "benchmarks": benchmark_results,
        "pagination_verified": {
            "has_total_header": has_total_header,
            "total_count": total_count,
            "page_size_adhered": len(st_json) <= 15,
        },
        "security_findings": {
            "expired_token_rejected": True,
            "profile_cache_ttl_seconds": _profile_cache.ttl,
            "cache_window_observed": cache_window_active,
            "invalidation_effective": res_deactivated_post_invalidate.status_code in (401, 403),
            "multi_worker_implication": "In multi-worker deployment (e.g. Uvicorn --workers 4), in-memory cache is local per-process. A cluster-wide invalidation or shorter TTL (e.g. 15-30s) is recommended for strict real-time revocation guarantees.",
        }
    }

    with open("docs/performance/backend_audit_data.json", "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2)
    print("\nBackend audit data saved to docs/performance/backend_audit_data.json")

if __name__ == "__main__":
    run_backend_audit()
