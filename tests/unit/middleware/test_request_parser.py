"""Tests for src.middleware.request_parser."""

import pytest

from src.middleware.error_handler import ValidationError
from src.middleware.request_parser import (
    get_user_id,
    parse_body,
    parse_path_params,
    parse_query_params,
)


class TestParseBody:
    def test_empty_body(self):
        assert parse_body({}) == {}

    def test_dict_body(self):
        assert parse_body({"body": {"a": 1}}) == {"a": 1}

    def test_valid_json_string(self):
        assert parse_body({"body": '{"a": 1}'}) == {"a": 1}

    def test_invalid_json_raises(self):
        with pytest.raises(ValidationError):
            parse_body({"body": "not json"})


class TestParsePathParams:
    def test_missing(self):
        assert parse_path_params({}) == {}

    def test_present(self):
        assert parse_path_params({"pathParameters": {"id": "123"}}) == {"id": "123"}


class TestParseQueryParams:
    def test_missing(self):
        assert parse_query_params({}) == {}

    def test_present(self):
        assert parse_query_params({"queryStringParameters": {"limit": "10"}}) == {"limit": "10"}


class TestGetUserId:
    def test_missing(self):
        assert get_user_id({}) is None

    def test_present(self):
        event = {"requestContext": {"authorizer": {"claims": {"sub": "user-123"}}}}
        assert get_user_id(event) == "user-123"
