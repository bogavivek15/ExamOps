"""
ExamOps Independent Scheduling RBAC Verification Script
Validates:
1. Dedicated operator login (ACADEMIC_ADMINISTRATOR / EXAM_OFFICER) -> POST /api/scheduling/runs succeeds (HTTP 200/201).
2. Learner login (LEARNER) -> POST /api/scheduling/runs returns HTTP 403 Forbidden with clear permission message.
3. Anti-Spoofing: Client header/body injection cannot override database-backed user role.
4. JWT Signature Verification: Tampered token returns HTTP 401 Unauthorized.
5. Unauthenticated: Missing token returns HTTP 401 Unauthorized.
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def make_request(endpoint, method="GET", headers=None, data=None):
    url = f"{BASE_URL}{endpoint}"
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    
    encoded_data = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=encoded_data, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            parsed = json.loads(body) if body else {}
            return status, parsed
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed

def run_tests():
    print("=" * 70)
    print("EXAMOPS SCHEDULING RBAC VERIFICATION SUITE")
    print("=" * 70)

    # 1. Healthcheck
    status, data = make_request("/health")
    print(f"[*] API Healthcheck: HTTP {status} (status={data.get('status')})")
    assert status == 200, f"API not healthy: {status}"

    period_id = "11111111-1111-1111-1111-111111111111"

    # =========================================================================
    # TEST CASE 1: Dedicated Operator (ACADEMIC_ADMINISTRATOR) Creating a Run
    # =========================================================================
    print("\n--- TEST CASE 1: Authorized Operator (ACADEMIC_ADMINISTRATOR) ---")
    login_payload = {
        "email": "exam.officer@examops.institution.edu",
        "password": "dev-password"
    }
    status, auth_res = make_request("/api/auth/login", method="POST", data=login_payload)
    print(f"[*] Operator Login Response: HTTP {status}")
    assert status == 200, f"Operator login failed: {auth_res}"
    operator_token = auth_res["access_token"]
    user_info = auth_res["user"]
    print(f"    User ID: {user_info['id']}")
    print(f"    Role: {user_info['role']}")
    print(f"    Name: {user_info.get('display_name')}")
    assert user_info["role"] in ["ACADEMIC_ADMINISTRATOR", "EXAM_OFFICER", "PLATFORM_ADMINISTRATOR", "SUPER_ADMIN"]

    # Attempt to create a scheduling run with operator token
    run_payload = {
        "academic_period_id": period_id,
        "algorithm_version": "1.0.0-rbac-verify",
        "seed": 20261022
    }
    status, run_res = make_request(
        "/api/scheduling/runs",
        method="POST",
        headers={"Authorization": f"Bearer {operator_token}"},
        data=run_payload
    )
    print(f"[*] Create Scheduling Run (Operator): HTTP {status}")
    print(f"    Response: {json.dumps(run_res, indent=2)}")
    assert status in [200, 201], f"Expected HTTP 200/201 but got {status}: {run_res}"
    assert "id" in run_res, "Run response missing 'id'"
    assert "run_code" in run_res, "Run response missing 'run_code'"
    assert run_res["status"] == "DRAFT", f"Unexpected status: {run_res['status']}"
    print(f"[PASS] Operator successfully created scheduling run: {run_res['run_code']}")

    # =========================================================================
    # TEST CASE 2: Unauthorized Learner (LEARNER) Attempting to Create a Run
    # =========================================================================
    print("\n--- TEST CASE 2: Unauthorized User (LEARNER) ---")
    learner_login = {
        "email": "maya.muller.0001@student.institution.edu",
        "password": "dev-password"
    }
    status, auth_res = make_request("/api/auth/login", method="POST", data=learner_login)
    print(f"[*] Learner Login Response: HTTP {status}")
    assert status == 200, f"Learner login failed: {auth_res}"
    learner_token = auth_res["access_token"]
    learner_info = auth_res["user"]
    print(f"    User ID: {learner_info['id']}")
    print(f"    Role: {learner_info['role']}")
    print(f"    Name: {learner_info.get('display_name')}")
    assert learner_info["role"] == "LEARNER", f"Expected LEARNER but got {learner_info['role']}"

    # Attempt to create scheduling run with learner token
    status, err_res = make_request(
        "/api/scheduling/runs",
        method="POST",
        headers={"Authorization": f"Bearer {learner_token}"},
        data=run_payload
    )
    print(f"[*] Create Scheduling Run (Learner): HTTP {status}")
    print(f"    Response: {err_res}")
    assert status == 403, f"Expected HTTP 403 Forbidden for LEARNER, but got {status}: {err_res}"
    detail_msg = err_res.get("detail", "")
    assert "role 'LEARNER' lacks permission" in detail_msg, f"Unexpected error detail: {detail_msg}"
    print(f"[PASS] Learner correctly rejected with HTTP 403 Forbidden: '{detail_msg}'")

    # =========================================================================
    # TEST CASE 3: Client Role Spoofing Prevention
    # =========================================================================
    print("\n--- TEST CASE 3: Client Role Spoofing Prevention ---")
    spoof_headers = {
        "Authorization": f"Bearer {learner_token}",
        "X-Test-Role": "ACADEMIC_ADMINISTRATOR",
        "X-User-Role": "EXAM_OFFICER",
        "Role": "SUPER_ADMIN"
    }
    spoof_payload = dict(run_payload)
    spoof_payload["role"] = "ACADEMIC_ADMINISTRATOR"
    
    status, spoof_res = make_request(
        "/api/scheduling/runs",
        method="POST",
        headers=spoof_headers,
        data=spoof_payload
    )
    print(f"[*] Spoofing Attempt Response: HTTP {status}")
    print(f"    Response: {spoof_res}")
    assert status == 403, f"CRITICAL SECURITY DEFECT: Spoofed headers bypassed RBAC! Got HTTP {status}"
    assert "role 'LEARNER' lacks permission" in spoof_res.get("detail", "")
    print("[PASS] Role spoofing defeated: Backend enforces PostgreSQL database user_profiles.role")

    # =========================================================================
    # TEST CASE 4: Tampered JWT Signature
    # =========================================================================
    print("\n--- TEST CASE 4: Tampered JWT Token Signature ---")
    parts = learner_token.split(".")
    # Tamper with payload portion
    tampered_token = f"{parts[0]}.eyJzdWIiOiAiZWUwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAxIiwgInJvbGUiOiAiU1VQRVJfQURNSU4ifQ.{parts[2]}"
    status, tampered_res = make_request(
        "/api/scheduling/runs",
        method="POST",
        headers={"Authorization": f"Bearer {tampered_token}"},
        data=run_payload
    )
    print(f"[*] Tampered Token Response: HTTP {status}")
    print(f"    Response: {tampered_res}")
    assert status == 401, f"Expected HTTP 401 Unauthorized for tampered token, got {status}"
    print("[PASS] Tampered JWT signature properly rejected with HTTP 401 Unauthorized")

    # =========================================================================
    # TEST CASE 5: Missing Authentication Header
    # =========================================================================
    print("\n--- TEST CASE 5: Unauthenticated Request ---")
    status, unauth_res = make_request(
        "/api/scheduling/runs",
        method="POST",
        data=run_payload
    )
    print(f"[*] Unauthenticated Request Response: HTTP {status}")
    print(f"    Response: {unauth_res}")
    assert status == 401, f"Expected HTTP 401 Unauthorized for missing auth header, got {status}"
    print("[PASS] Unauthenticated request properly rejected with HTTP 401 Unauthorized")

    print("\n" + "=" * 70)
    print("ALL 5 SCHEDULING RBAC VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n[FAIL] Test execution encountered error: {e}", file=sys.stderr)
        sys.exit(1)
