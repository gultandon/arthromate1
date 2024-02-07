"""Tests for src.services.user."""

from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from src.middleware.error_handler import NotFoundError, ValidationError
from src.services.user import get_or_create_user, get_user, update_user_profile


class TestGetOrCreateUser:
    @patch("src.services.user.user_model.get_by_id")
    @patch("src.services.user.user_model.create")
    def test_create_new(self, mock_create, mock_get):
        mock_get.return_value = None
        mock_create.return_value = None
        user = get_or_create_user("u1")
        assert user["userId"] == "u1"
        mock_create.assert_called_once()

    @patch("src.services.user.user_model.get_by_id")
    def test_existing(self, mock_get):
        mock_get.return_value = {"userId": "u1"}
        assert get_or_create_user("u1") == {"userId": "u1"}

    @patch("src.services.user.user_model.get_by_id")
    @patch("src.services.user.user_model.create")
    def test_race_condition(self, mock_create, mock_get):
        mock_get.side_effect = [None, {"userId": "u1"}]
        error_response = {"Error": {"Code": "ConditionalCheckFailedException"}}
        mock_create.side_effect = ClientError(error_response, "PutItem")
        user = get_or_create_user("u1")
        assert user == {"userId": "u1"}


class TestGetUser:
    @patch("src.services.user.user_model.get_by_id")
    def test_found(self, mock_get):
        mock_get.return_value = {"userId": "u1"}
        assert get_user("u1") == {"userId": "u1"}

    @patch("src.services.user.user_model.get_by_id")
    def test_not_found(self, mock_get):
        mock_get.return_value = None
        with pytest.raises(NotFoundError):
            get_user("u1")


class TestUpdateUserProfile:
    @patch("src.services.user.user_model.get_by_id")
    @patch("src.services.user.user_model.update")
    def test_success(self, mock_update, mock_get):
        mock_get.return_value = {"userId": "u1", "profile": {"name": "Old"}}
        mock_update.return_value = {"userId": "u1", "profile": {"name": "New"}}
        result = update_user_profile("u1", {"name": "New"})
        assert result["profile"]["name"] == "New"

    def test_invalid_data(self):
        with pytest.raises(ValidationError):
            update_user_profile("u1", None)
