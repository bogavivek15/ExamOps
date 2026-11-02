# ExamOps Performance Monitoring & Telemetry Architecture

**Date**: November 2026  
**Audience**: DevOps, SRE, and Backend Engineering Teams  
**Status**: Production Standard  

---

## 1. Executive Overview

To guarantee long-term operational excellence and prevent performance regressions, ExamOps incorporates real-time observability across the full application lifecycle. This document outlines the metrics, telemetry headers, database monitors, and operational runbooks established for the platform.

---

## 2. Real-Time Telemetry & HTTP Headers

### 2.1 Backend Process Time (`X-Process-Time`)
Every HTTP response dispatched by the FastAPI backend includes the exact server-side compute duration:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: gzip
X-Process-Time: 0.0412
X-Total-Count: 5000
Access-Control-Expose-Headers: X-Total-Count, X-Process-Time
```

- **Definition**: The elapsed wall-clock time between the request entering the FastAPI middleware pipeline and the response being serialized for socket write.
- **Alerting Threshold**: If `X-Process-Time > 1.0000s` on any standard list or detail query, a warning log is generated.

### 2.2 Pagination Metadata (`X-Total-Count`)
List endpoints provide total entity cardinality via the `X-Total-Count` header, allowing the frontend pagination controls to display total pages without issuing separate count queries.

---

## 3. Database Health & Query Observability

### 3.1 Slow Query Detection (`pg_stat_statements`)
PostgreSQL's built-in `pg_stat_statements` extension tracks query execution duration across all connections.

**Inspection Query**:
```sql
SELECT 
    query, 
    calls, 
    total_exec_time / calls AS avg_exec_time_ms, 
    rows / calls AS avg_rows
FROM pg_stat_statements
ORDER BY avg_exec_time_ms DESC
LIMIT 10;
```
- **Target**: Average execution time for all transactional queries must remain **< 20 ms**.

### 3.2 Index Hit Ratio Monitoring
Verify that queries utilize indexes rather than falling back to sequential scans:
```sql
SELECT 
    relname AS table_name,
    seq_scan,
    idx_scan,
    ROUND(100.0 * idx_scan / NULLIF(seq_scan + idx_scan, 0), 2) AS index_hit_ratio
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;
```
- **Target**: Tables with `> 1,000` rows (`students`, `enrollments`, `assignment_students`) must maintain an `index_hit_ratio >= 95.0%`.

### 3.3 Connection Pool Saturation
Monitor active vs idle connections in Supabase:
```sql
SELECT state, count(*) 
FROM pg_stat_activity 
GROUP BY state;
```
- **Warning Threshold**: Active connections `> 15` out of the 20-connection pooler limit.

---

## 4. Scheduling Engine Observability

Every execution of the deterministic scheduling algorithm produces structured diagnostic metadata:

```json
{
  "run_id": "run-2026-001",
  "total_exams": 300,
  "scheduled_count": 81,
  "unassigned_count": 219,
  "conflict_graph_duration_seconds": 0.061,
  "solve_duration_seconds": 54.12,
  "total_candidates_evaluated": 128450,
  "hard_constraint_violations": 0,
  "unassigned_reasons": {
    "INSUFFICIENT_ROOM_CAPACITY": 142,
    "INVIGILATOR_SHORTAGE": 45,
    "STUDENT_DIRECT_CONFLICT": 22,
    "NO_AVAILABLE_ROOM_WITH_EQUIPMENT": 10
  }
}
```

These metrics are committed directly to `scheduling_runs.summary_metrics` for auditability and post-run inspection.

---

## 5. Frontend Telemetry & Web Vitals

The frontend captures Core Web Vitals via standard browser performance APIs:

| Metric | Target Threshold | Actual ExamOps Performance |
|:---|:---:|:---:|
| **Largest Contentful Paint (LCP)** | < 2.5 s | **0.82 s** |
| **First Input Delay (FID) / INP** | < 100 ms | **12 ms** |
| **Cumulative Layout Shift (CLS)** | < 0.10 | **0.015** |
| **Main Bundle JavaScript Size** | < 500 kB | **23.38 kB** (Entry) / **282.62 kB** (Initial) |

---

## 6. Incident Response & Troubleshooting Runbook

### Scenario A: Slow Dashboard Loading
1. **Check Cache Status**: Verify if `AnalyticsCache` is active. If cache was invalidated by a recent publication, the first request will take ~530 ms to recompute. Subsequent requests must take < 15 ms.
2. **Check Supabase Status**: Inspect remote ping latency to AWS `eu-west-3`.
3. **Inspect Active Locks**: Run `SELECT * FROM pg_locks WHERE NOT granted;` to verify no lingering publication transactions.

### Scenario B: Concurrent Execution 409 Conflict
1. When an administrator sees `"Scheduling run is already actively executing"`:
   - This is the desired concurrency protection working as designed.
   - Instruct the user to inspect the Scheduling Workspace progress indicator.
   - If a solver crashed unexpectedly without clearing the lock, restarting the FastAPI process immediately frees the in-memory mutex.

