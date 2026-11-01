"""
ExamOps Database Connection & Query Layer
Provides direct PostgreSQL pooling via psycopg2 and Supabase client integration.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from typing import Generator, Any, List, Dict, Optional, Tuple
from backend.config import settings

# Threaded connection pool for PostgreSQL
_pool: Optional[ThreadedConnectionPool] = None

def init_db_pool(minconn: int = 1, maxconn: int = 20):
    global _pool
    if _pool is None:
        try:
            _pool = ThreadedConnectionPool(
                minconn=minconn,
                maxconn=maxconn,
                dsn=settings.DATABASE_URL,
            )
        except Exception as e:
            print(f"Warning: Could not connect to PostgreSQL pool at {settings.DATABASE_URL}: {e}")

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
            _pool.putconn(conn)
    else:
        # Direct fallback connection
        conn = psycopg2.connect(settings.DATABASE_URL)
        try:
            yield conn
        finally:
            conn.close()

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
