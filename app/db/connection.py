"""PostgreSQL connection pooling and schema bootstrap.

Every tool ultimately reads/writes through here. Credentials come only from
the DATABASE_URL environment variable -- never hardcoded.
"""
import os
from contextlib import contextmanager
from pathlib import Path

import psycopg2
import psycopg2.extras
from psycopg2 import pool

_pool = None


def _database_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Copy .env.example to .env and configure your PostgreSQL connection string."
        )
    return url


def _get_pool():
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(1, 10, dsn=_database_url())
    return _pool


@contextmanager
def get_connection():
    conn = _get_pool().getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _get_pool().putconn(conn)


@contextmanager
def get_cursor(dict_cursor=True):
    with get_connection() as conn:
        cursor_factory = psycopg2.extras.RealDictCursor if dict_cursor else None
        cur = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
        finally:
            cur.close()


def init_db():
    """Create tables/indexes if they don't already exist. Safe to call on every boot."""
    schema_path = Path(__file__).parent / "schema.sql"
    sql = schema_path.read_text()
    with get_cursor(dict_cursor=False) as cur:
        cur.execute(sql)
