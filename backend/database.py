"""
ExamOps Database Connection & Query Layer
Provides direct PostgreSQL pooling via psycopg2 and Supabase PostgreSQL integration.
"""
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from typing import Generator, Any, List, Dict, Optional, Tuple
from backend.config import settings

def mask_connection_url(url: str) -> str:
    """Masks database credentials in connection URIs for safe diagnostic logging."""
    if not url:
        return "<EMPTY_DATABASE_URL>"
    # Use robust regex matching from :// after scheme up to the last @ before host
    # e.g., postgresql://user:pass@word@host:5432/db -> postgresql://user:***@host:5432/db
    return re.sub(r"://([^:]+):.*@([^@/:]+)(:\d+)?(/.*)?$", r"://\1:***@\2\3\4", url)

# Threaded connection pool for PostgreSQL
_pool: Optional[ThreadedConnectionPool] = None

def init_db_pool(minconn: Optional[int] = None, maxconn: Optional[int] = None):
    global _pool
    if _pool is None:
        minconn = minconn or settings.DB_POOL_MIN_CONN
        maxconn = maxconn or settings.DB_POOL_MAX_CONN
        try:
            # Append connect_timeout if not already specified
            dsn = settings.DATABASE_URL
            _pool = ThreadedConnectionPool(
                minconn=minconn,
                maxconn=maxconn,
                dsn=dsn,
                connect_timeout=10,
            )
        except Exception as e:
            masked = mask_connection_url(settings.DATABASE_URL)
            print(f"Warning: Could not initialize PostgreSQL pool [{masked}]: {e}")

@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """Yields a database connection with auto-commit/rollback semantics."""
    global _pool
    if _pool is None:
        init_db_pool()
    
    if _pool is not None:
        conn = _pool.getconn()
        try:
            yield conn
        finally:
            try:
                if conn.closed:
                    _pool.putconn(conn, close=True)
                else:
                    try:
                        with conn.cursor() as cur:
                            cur.execute("SELECT pg_advisory_unlock_all();")
                    except Exception:
                        pass
                    _pool.putconn(conn)
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
    else:
        # Direct fallback connection
        try:
            conn = psycopg2.connect(settings.DATABASE_URL, connect_timeout=10)
            try:
                yield conn
            finally:
                conn.close()
        except Exception as e:
            masked = mask_connection_url(settings.DATABASE_URL)
            raise ConnectionError(f"Database connection failed [{masked}]: {e}") from None

@contextmanager
def get_db_cursor(commit: bool = False) -> Generator[RealDictCursor, None, None]:
    """Yields a dictionary cursor for executing queries."""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

def execute_query(sql: str, params: Optional[Tuple[Any, ...]] = None, fetch_one: bool = False) -> Any:
    """Executes a SELECT query and returns dictionary results."""
    with get_db_cursor() as cur:
        cur.execute(sql, params)
        if fetch_one:
            return cur.fetchone()
        return cur.fetchall()

def execute_mutation(sql: str, params: Optional[Tuple[Any, ...]] = None) -> int:
    """Executes an INSERT, UPDATE, or DELETE query and returns rowcount."""
    with get_db_cursor(commit=True) as cur:
        cur.execute(sql, params)
        return cur.rowcount
