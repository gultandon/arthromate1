"""Integration tests for Lambda handlers."""

from unittest.mock import MagicMock, patch

import pytest

from src.handlers.create_pain_report import handler as create_handler
from src.handlers.delete_pain_report import handler as delete_handler
from src.handlers.get_pain_report import handler as get_handler
from src.handlers.get_user_profile import handler as get_user_handler
from src.handlers.list_pain_reports import handler as list_handler
from src.handlers.update_user_profile import handler as update_user_handler


def _auth_event(body=None, path_params=None, query_params=None):
    event = {
        "requestContext": {
            "authorizer": {"claims": {"sub": "integration-user-123"}}
        },
    }
    if body is not None:
        event["body"] = body
    if path_params is not None:
        event["pathParameters"] = path_params
    if query_params is not None:
        event["queryStringParameters"] = query_params
    return event


class TestCreatePainReport:
    @patch("src.services.pain_report.pain_report_model.create")
    def test_success(self, mock_create):
        mock_create.return_value = None
        event = _auth_event(body={"painLevel": 5, "affectedJoints": ["left_knee"]})
        result = create_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 201
        assert result["body"]["success"] is True

    @patch("src.services.pain_report.pain_report_model.create")
    def test_validation_error(self, mock_create):
        event = _auth_event(body={"painLevel": 15, "affectedJoints": ["left_knee"]})
        result = create_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 400

    def test_unauthorized(self):
        event = {"body": {"painLevel": 5, "affectedJoints": ["left_knee"]}}
        result = create_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 401


class TestGetPainReport:
    @patch("src.services.pain_report.pain_report_model.get_by_id")
    def test_found(self, mock_get):
        mock_get.return_value = {"reportId": "r1", "userId": "integration-user-123"}
        event = _auth_event(path_params={"reportId": "r1"})
        result = get_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 200

    @patch("src.services.pain_report.pain_report_model.get_by_id")
    def test_not_found(self, mock_get):
        mock_get.return_value = None
        event = _auth_event(path_params={"reportId": "missing"})
        result = get_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 404


class TestListPainReports:
    @patch("src.services.pain_report.pain_report_model.list_by_user")
    def test_list(self, mock_list):
        mock_list.return_value = [{"reportId": "r1"}]
        event = _auth_event()
        result = list_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 200
        assert result["body"]["data"]["count"] == 1


class TestDeletePainReport:
    @patch("src.services.pain_report.pain_report_model.remove")
    def test_success(self, mock_remove):
        mock_remove.return_value = {"reportId": "r1"}
        event = _auth_event(path_params={"reportId": "r1"})
        result = delete_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 200

    @patch("src.services.pain_report.pain_report_model.remove")
    def test_not_found(self, mock_remove):
        mock_remove.return_value = None
        event = _auth_event(path_params={"reportId": "missing"})
        result = delete_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 404


class TestGetUserProfile:
    @patch("src.services.user.user_model.get_by_id")
    def test_found(self, mock_get):
        mock_get.return_value = {"userId": "integration-user-123"}
        event = _auth_event()
        result = get_user_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 200

    @patch("src.services.user.user_model.get_by_id")
    def test_not_found(self, mock_get):
        mock_get.return_value = None
        event = _auth_event()
        result = get_user_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 404


class TestUpdateUserProfile:
    @patch("src.services.user.user_model.get_by_id")
    @patch("src.services.user.user_model.update")
    def test_success(self, mock_update, mock_get):
        mock_get.return_value = {"userId": "integration-user-123", "profile": {}}
        mock_update.return_value = {"userId": "integration-user-123", "profile": {"name": "New"}}
        event = _auth_event(body={"name": "New"})
        result = update_user_handler(event, MagicMock(aws_request_id="aws-req-1"))
        assert result["statusCode"] == 200
