"""Tests for src.utils.response_builder."""

import pytest

from src.utils.response_builder import error, success


class TestSuccess:
    def test_returns_200_by_default(self):
        result = success({"foo": "bar"})
        assert result["statusCode"] == 200

    def test_returns_custom_status_code(self):
        result = success({"foo": "bar"}, 201)
        assert result["statusCode"] == 201

    def test_envelope_format(self):
        result = success({"foo": "bar"})
        assert result["body"]["success"] is True
        assert result["body"]["data"] == {"foo": "bar"}
        assert result["body"]["error"] is None

    def test_cors_headers(self):
        result = success({})
        assert result["headers"]["Content-Type"] == "application/json"
        assert result["headers"]["Access-Control-Allow-Origin"] == "*"


class TestError:
    def test_returns_500_by_default(self):
        result = error("Something went wrong")
        assert result["statusCode"] == 500

    def test_returns_custom_status_code(self):
        result = error("Not found", 404)
        assert result["statusCode"] == 404

    def test_envelope_format(self):
        result = error("Not found", 404, {"code": "NOT_FOUND"})
        assert result["body"]["success"] is False
        assert result["body"]["data"] is None
        assert result["body"]["error"]["message"] == "Not found"
        assert result["body"]["error"]["details"] == {"code": "NOT_FOUND"}

    def test_cors_headers(self):
        result = error("Oops")
        assert result["headers"]["Content-Type"] == "application/json"
        assert result["headers"]["Access-Control-Allow-Origin"] == "*"
