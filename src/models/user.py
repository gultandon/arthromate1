"""User MySQL model."""

import json

from src.models.db import get_connection


def create(user: dict) -> dict:
    """Insert a new user, silently ignoring duplicate userId."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT IGNORE INTO users (userId, email, createdAt, updatedAt, profile)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user["userId"],
                user.get("email"),
                user.get("createdAt"),
                user.get("updatedAt"),
                json.dumps(user.get("profile", {})),
            ),
        )
    return user


def get_by_id(user_id: str) -> dict | None:
    """Fetch a user by ID."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE userId = %s", (user_id,))
        row = cur.fetchone()
    return _deserialize(row) if row else None


def update(user_id: str, updates: dict) -> dict:
    """Update a user's attributes and return the updated row."""
    if not updates:
        return get_by_id(user_id) or {}

    set_clauses = ", ".join(f"`{key}` = %s" for key in updates)
    values = [
        json.dumps(v) if isinstance(v, (dict, list)) else v for v in updates.values()
    ]
    values.append(user_id)

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(f"UPDATE users SET {set_clauses} WHERE userId = %s", values)
        cur.execute("SELECT * FROM users WHERE userId = %s", (user_id,))
        row = cur.fetchone()
    return _deserialize(row) if row else {}


def _deserialize(row: dict) -> dict:
    if row.get("profile") and isinstance(row["profile"], str):
        row["profile"] = json.loads(row["profile"])
    return row
