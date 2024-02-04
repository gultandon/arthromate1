"""Tests for src.models.user."""

import json
from unittest.mock import MagicMock, patch

from src.models import user as user_model


def _make_cursor_ctx(mock_cursor):
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=mock_cursor)
    cm.__exit__ = MagicMock(return_value=False)
    return cm


def _mock_conn(mock_cursor):
    conn = MagicMock()
    conn.cursor.return_value = _make_cursor_ctx(mock_cursor)
    return conn


class TestCreate:
    def test_create(self):
        cur = MagicMock()
        conn = _mock_conn(cur)
        user = {"userId": "u1", "email": "a@b.com", "createdAt": "ts", "updatedAt": "ts", "profile": {}}
        with patch("src.models.user.get_connection", return_value=conn):
            result = user_model.create(user)
        cur.execute.assert_called_once()
        assert result == user


class TestGetById:
    def test_found(self):
        cur = MagicMock()
        cur.fetchone.return_value = {"userId": "u1", "profile": json.dumps({})}
        conn = _mock_conn(cur)
        with patch("src.models.user.get_connection", return_value=conn):
            result = user_model.get_by_id("u1")
        assert result == {"userId": "u1", "profile": {}}

    def test_not_found(self):
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = _mock_conn(cur)
        with patch("src.models.user.get_connection", return_value=conn):
            assert user_model.get_by_id("u1") is None


class TestUpdate:
    def test_update(self):
        cur = MagicMock()
        cur.fetchone.return_value = {"userId": "u1", "profile": json.dumps({})}
        conn = _mock_conn(cur)
        with patch("src.models.user.get_connection", return_value=conn):
            result = user_model.update("u1", {"profile": {}})
        assert result == {"userId": "u1", "profile": {}}
        assert cur.execute.call_count == 2
