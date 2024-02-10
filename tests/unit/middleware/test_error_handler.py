"""Tests for src.middleware.error_handler."""

import pytest

from src.middleware.error_handler import (
    AppError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


class TestAppError:
    def test_default_values(self):
        err = AppError("boom")
        assert err.status_code == 500
        assert err.code == "INTERNAL_ERROR"
        assert str(err) == "boom"

    def test_custom_values(self):
        err = AppError("oops", 418, "TEAPOT")
        assert err.status_code == 418
        assert err.code == "TEAPOT"


class TestValidationError:
    def test_defaults(self):
        err = ValidationError("bad input")
        assert err.status_code == 400
        assert err.code == "VALIDATION_ERROR"


class TestNotFoundError:
    def test_defaults(self):
        err = NotFoundError("missing")
        assert err.status_code == 404
        assert err.code == "NOT_FOUND"


class TestUnauthorizedError:
    def test_defaults(self):
        err = UnauthorizedError()
        assert err.status_code == 401
        assert err.code == "UNAUTHORIZED"

    def test_custom_message(self):
        err = UnauthorizedError("go away")
        assert str(err) == "go away"


class TestConflictError:
    def test_defaults(self):
        err = ConflictError("dup")
        assert err.status_code == 409
        assert err.code == "CONFLICT"
