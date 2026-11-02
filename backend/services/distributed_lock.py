"""
ExamOps Distributed Advisory Lock Manager
Provides PostgreSQL-backed distributed locking for multi-worker and multi-process deployments.
Uses session-level PostgreSQL advisory locks with autocommit=True to ensure:
- Mutual exclusion across multiple Uvicorn workers and multi-container instances.
- Zero open transactions during execution (eliminates idle-in-transaction connection stalls).
- Immediate non-blocking conflict detection (HTTP 409).
- Automatic lock release by PostgreSQL kernel if a worker crashes or socket drops.
- Clean lock release and connection state restoration on completion or exception.
"""
from contextlib import contextmanager
import hashlib
from typing import Generator, Optional
from backend.database import get_db_connection

class DistributedLockConflictError(Exception):
    """Raised when a distributed advisory lock cannot be acquired because another worker holds it."""
    def __init__(self, resource: str, detail: Optional[str] = None):
        msg = detail or f"Resource '{resource}' is currently locked by another active process."
        super().__init__(msg)
        self.resource = resource
        self.detail = msg

def hash_to_postgres_bigint(key_str: str) -> int:
    """
    Computes a deterministic 64-bit signed integer for PostgreSQL pg_try_advisory_lock.
    Uses SHA-256 truncated to 8 bytes, parsed as a signed 64-bit integer (-2^63 to 2^63 - 1).
    """
    digest = hashlib.sha256(key_str.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=True)

@contextmanager
def distributed_advisory_lock(resource_key: str, namespace: str = "scheduling_run") -> Generator[int, None, None]:
    """
    Acquires a PostgreSQL session-level advisory lock on a dedicated connection with autocommit=True.
    
    Yields the integer lock ID if acquired.
    Raises DistributedLockConflictError immediately if another worker holds the lock.
    Guarantees lock release and connection restoration in finally blocks.
    """
    full_key = f"{namespace}:{resource_key}"
    lock_id = hash_to_postgres_bigint(full_key)
    
    with get_db_connection() as conn:
        orig_autocommit = conn.autocommit
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_try_advisory_lock(%s);", (lock_id,))
                row = cur.fetchone()
                acquired = bool(row[0]) if row else False
            
            if not acquired:
                raise DistributedLockConflictError(
                    resource=resource_key,
                    detail=f"Resource '{resource_key}' is actively being processed by another worker.",
                )
            
            lock_confirmed_released = False
            try:
                yield lock_id
            finally:
                try:
                    with conn.cursor() as cur:
                        cur.execute("SELECT pg_advisory_unlock(%s);", (lock_id,))
                        row = cur.fetchone()
                        if row and row[0]:
                            lock_confirmed_released = True
                except Exception:
                    lock_confirmed_released = False

                if not lock_confirmed_released:
                    # Discard the connection completely so it is never returned to the pool
                    # with an uncertain advisory-lock state. Closing the connection causes
                    # PostgreSQL to immediately drop all session locks.
                    try:
                        conn.close()
                    except Exception:
                        pass
        finally:
            if not conn.closed:
                conn.autocommit = orig_autocommit

