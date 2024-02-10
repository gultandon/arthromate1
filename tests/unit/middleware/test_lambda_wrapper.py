"""Tests for src.middleware.lambda_wrapper."""

from unittest.mock import MagicMock

import pytest

from src.middleware.error_handler import AppError, ValidationError
from src.middleware.lambda_wrapper import wrap_handler


class TestWrapHandler:
    def test_successful_invocation(self):
        def handler(event, context):
            return {"statusCode": 200, "body": "ok"}

        wrapped = wrap_handler(handler, "testFn")
        result = wrapped({}, MagicMock(aws_request_id="req-1"))
        assert result["statusCode"] == 200

    def test_app_error_caught(self):
        def handler(event, context):
            raise ValidationError("bad")

        wrapped = wrap_handler(handler, "testFn")
        result = wrapped({}, MagicMock(aws_request_id="req-1"))
        assert result["statusCode"] == 400
        assert result["body"]["error"]["details"]["code"] == "VALIDATION_ERROR"

    def test_unknown_error_caught(self):
        def handler(event, context):
            raise RuntimeError("oops")

        wrapped = wrap_handler(handler, "testFn")
        result = wrapped({}, MagicMock(aws_request_id="req-1"))
        assert result["statusCode"] == 500
        assert result["body"]["error"]["message"] == "Internal server error"
