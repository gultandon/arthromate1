"""Pain Report MySQL model.

Access patterns:
- Get all reports for a user (indexed by userId + timestamp)
- Get a single report by ID
- Query reports in a date range for a user
"""

import json
from typing import Any

from src.models.db import get_connection


def create(report: dict) -> dict:
    """Insert a new pain report."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO pain_reports
                (reportId, userId, timestamp, painLevel, affectedJoints, notes, mobility)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                report["reportId"],
                report["userId"],
                report["timestamp"],
                report["painLevel"],
                json.dumps(report["affectedJoints"]),
                report.get("notes"),
                report.get("mobility"),
            ),
        )
    return report


def get_by_id(report_id: str, user_id: str) -> dict | None:
    """Fetch a single report by ID for a given user."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM pain_reports WHERE reportId = %s AND userId = %s",
            (report_id, user_id),
        )
        row = cur.fetchone()
    return _deserialize(row) if row else None


def list_by_user(user_id: str, options: dict | None = None) -> list[dict]:
    """List pain reports for a user, optionally filtered by date range."""
    options = options or {}
    start_date = options.get("startDate")
    end_date = options.get("endDate")
    limit = options.get("limit", 50)

    sql = "SELECT * FROM pain_reports WHERE userId = %s"
    params: list[Any] = [user_id]

    if start_date and end_date:
        sql += " AND timestamp BETWEEN %s AND %s"
        params += [start_date, end_date]
    elif start_date:
        sql += " AND timestamp >= %s"
        params.append(start_date)
    elif end_date:
        sql += " AND timestamp <= %s"
        params.append(end_date)

    sql += " ORDER BY timestamp DESC LIMIT %s"
    params.append(limit)

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return [_deserialize(row) for row in rows]


def remove(report_id: str, user_id: str) -> dict | None:
    """Delete a pain report by ID for a given user."""
    item = get_by_id(report_id, user_id)
    if not item:
        return None
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM pain_reports WHERE reportId = %s AND userId = %s",
            (report_id, user_id),
        )
    return item


def _deserialize(row: dict) -> dict:
    if row.get("affectedJoints") and isinstance(row["affectedJoints"], str):
        row["affectedJoints"] = json.loads(row["affectedJoints"])
    return row
