"""
Measure API endpoint latency baselines for ExamOps.
Tests p50, p95, and average latency over multiple iterations.
"""
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
headers = {"X-Test-Role": "ACADEMIC_ADMINISTRATOR"}

endpoints = [
    ("/health", {}),
    ("/api/analytics/overview", headers),
    ("/api/students?limit=15", headers),
    ("/api/students?limit=50", headers),
    ("/api/students?limit=15&search=John", headers),
    ("/api/courses?limit=15", headers),
    ("/api/courses?limit=50", headers),
    ("/api/exams?limit=15", headers),
    ("/api/exams?limit=50", headers),
    ("/api/rooms?limit=15", headers),
    ("/api/invigilators?limit=15", headers),
    ("/api/accommodations?limit=15", headers),
    ("/api/scheduling/runs?limit=10", headers),
    ("/api/audit/logs?limit=15", headers),
]

# Warm-up call
client.get("/health")

print(f"{'Endpoint':<42} | {'Status':<6} | {'Avg (ms)':<10} | {'Min (ms)':<10} | {'Max (ms)':<10}")
print("-" * 42 + "-+-" + "-" * 6 + "-+-" + "-" * 10 + "-+-" + "-" * 10 + "-+-" + "-" * 10)

results = []
for url, h in endpoints:
    times = []
    status = 0
    # 5 samples each
    for _ in range(5):
        t0 = time.perf_counter()
        res = client.get(url, headers=h)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
        status = res.status_code
    avg_t = sum(times) / len(times)
    min_t = min(times)
    max_t = max(times)
    print(f"{url:<42} | {status:<6} | {avg_t:10.2f} | {min_t:10.2f} | {max_t:10.2f}")
    results.append((url, status, avg_t, min_t, max_t))
