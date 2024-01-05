"""MySQL connection manager.

All database connections are centralized here. The module-level _connection
is reused across Lambda warm invocations; ping(reconnect=True) handles
dropped connections after idle periods.
"""

import os

import pymysql
import pymysql.cursors

_DB_HOST = os.environ.get("DB_HOST", "localhost")
_DB_PORT = int(os.environ.get("DB_PORT", "3306"))
_DB_USER = os.environ.get("DB_USER", "arthromate")
_DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
_DB_NAME = os.environ.get("DB_NAME", "arthromate")

_connection: pymysql.Connection | None = None


def get_connection() -> pymysql.Connection:
    """Return a live MySQL connection, reconnecting if needed."""
    global _connection
    try:
        if _connection is not None:
            _connection.ping(reconnect=True)
            return _connection
    except Exception:
        pass
    _connection = pymysql.connect(
        host=_DB_HOST,
        port=_DB_PORT,
        user=_DB_USER,
        password=_DB_PASSWORD,
        database=_DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=5,
    )
    return _connection


__all__ = ["get_connection"]
