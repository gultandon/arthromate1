"""Tests for src.models.pain_report."""

import json
from unittest.mock import MagicMock, patch

from src.models import pain_report as pain_report_model


def _make_cursor_ctx(mock_cursor):
    """Return a context-manager mock that yields mock_cursor."""
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
        report = {
            "reportId": "r1",
            "userId": "u1",
            "timestamp": "2024-01-01T00:00:00+00:00",
            "painLevel": 5,
            "affectedJoints": ["left_knee"],
            "notes": None,
            "mobility": None,
        }
        with patch("src.models.pain_report.get_connection", return_value=conn):
            result = pain_report_model.create(report)
        cur.execute.assert_called_once()
        assert result == report


class TestGetById:
    def test_found(self):
        cur = MagicMock()
        cur.fetchone.return_value = {
            "reportId": "r1",
            "userId": "u1",
            "affectedJoints": json.dumps(["left_knee"]),
        }
        conn = _mock_conn(cur)
        with patch("src.models.pain_report.get_connection", return_value=conn):
            result = pain_report_model.get_by_id("r1", "u1")
        assert result["reportId"] == "r1"
        assert result["affectedJoints"] == ["left_knee"]

    def test_not_found(self):
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = _mock_conn(cur)
        with patch("src.models.pain_report.get_connection", return_value=conn):
            assert pain_report_model.get_by_id("r1", "u1") is None


class TestListByUser:
    def test_basic(self):
        cur = MagicMock()
        cur.fetchall.return_value = [
            {"reportId": "r1", "affectedJoints": json.dumps(["left_knee"])}
        ]
        conn = _mock_conn(cur)
        with patch("src.models.pain_report.get_connection", return_value=conn):
            result = pain_report_model.list_by_user("u1")
        assert len(result) == 1

    def test_with_date_range(self):
        cur = MagicMock()
        cur.fetchall.return_value = []
        conn = _mock_conn(cur)
        with patch("src.models.pain_report.get_connection", return_value=conn):
            pain_report_model.list_by_user("u1", {"startDate": "2024-01-01", "endDate": "2024-12-31"})
        sql = cur.execute.call_args[0][0]
        assert "BETWEEN" in sql


class TestRemove:
    def test_success(self):
        cur = MagicMock()
        existing = {"reportId": "r1", "userId": "u1", "affectedJoints": json.dumps(["left_knee"])}
        cur.fetchone.return_value = existing
        conn = _mock_conn(cur)
        with patch("src.models.pain_report.get_connection", return_value=conn):
            result = pain_report_model.remove("r1", "u1")
        assert result["reportId"] == "r1"

    def test_not_found(self):
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = _mock_conn(cur)
        with patch("src.models.pain_report.get_connection", return_value=conn):
            assert pain_report_model.remove("r1", "u1") is None
