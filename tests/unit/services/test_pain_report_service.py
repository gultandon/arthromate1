"""Tests for src.services.pain_report."""

from unittest.mock import patch

import pytest

from src.middleware.error_handler import NotFoundError, ValidationError
from src.services.pain_report import (
    create_pain_report,
    delete_pain_report,
    get_pain_report,
    list_pain_reports,
)


class TestCreatePainReport:
    @patch("src.services.pain_report.pain_report_model.create")
    def test_success(self, mock_create):
        data = {"painLevel": 5, "affectedJoints": ["left_knee"]}
        result = create_pain_report("u1", data)
        assert result["userId"] == "u1"
        assert result["painLevel"] == 5
        mock_create.assert_called_once()

    def test_invalid_pain_level_high(self):
        with pytest.raises(ValidationError):
            create_pain_report("u1", {"painLevel": 11, "affectedJoints": ["left_knee"]})

    def test_invalid_pain_level_low(self):
        with pytest.raises(ValidationError):
            create_pain_report("u1", {"painLevel": -1, "affectedJoints": ["left_knee"]})

    def test_invalid_pain_level_type(self):
        with pytest.raises(ValidationError):
            create_pain_report("u1", {"painLevel": "five", "affectedJoints": ["left_knee"]})

    def test_empty_joints(self):
        with pytest.raises(ValidationError):
            create_pain_report("u1", {"painLevel": 5, "affectedJoints": []})

    def test_invalid_joint(self):
        with pytest.raises(ValidationError):
            create_pain_report("u1", {"painLevel": 5, "affectedJoints": ["left_toe"]})

    def test_invalid_mobility(self):
        with pytest.raises(ValidationError):
            create_pain_report("u1", {"painLevel": 5, "affectedJoints": ["left_knee"], "mobility": "super"})

    def test_notes_too_long(self):
        with pytest.raises(ValidationError):
            create_pain_report("u1", {"painLevel": 5, "affectedJoints": ["left_knee"], "notes": "x" * 1001})


class TestGetPainReport:
    @patch("src.services.pain_report.pain_report_model.get_by_id")
    def test_found(self, mock_get):
        mock_get.return_value = {"reportId": "r1"}
        assert get_pain_report("u1", "r1") == {"reportId": "r1"}

    @patch("src.services.pain_report.pain_report_model.get_by_id")
    def test_not_found(self, mock_get):
        mock_get.return_value = None
        with pytest.raises(NotFoundError):
            get_pain_report("u1", "r1")


class TestListPainReports:
    @patch("src.services.pain_report.pain_report_model.list_by_user")
    def test_list(self, mock_list):
        mock_list.return_value = [{"reportId": "r1"}]
        result = list_pain_reports("u1")
        assert len(result) == 1


class TestDeletePainReport:
    @patch("src.services.pain_report.pain_report_model.remove")
    def test_success(self, mock_remove):
        mock_remove.return_value = {"reportId": "r1"}
        assert delete_pain_report("u1", "r1") == {"reportId": "r1"}

    @patch("src.services.pain_report.pain_report_model.remove")
    def test_not_found(self, mock_remove):
        mock_remove.return_value = None
        with pytest.raises(NotFoundError):
            delete_pain_report("u1", "r1")
