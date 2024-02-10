"""Tests for src.middleware.auth."""

import pytest

from src.middleware.auth import require_auth
from src.middleware.error_handler import UnauthorizedError


class TestRequireAuth:
    def test_valid_auth(self):
        event = {"requestContext": {"authorizer": {"claims": {"sub": "user-123"}}}}
        assert require_auth(event) == "user-123"

    def test_missing_claims(self):
        with pytest.raises(UnauthorizedError):
            require_auth({})

    def test_missing_sub(self):
        event = {"requestContext": {"authorizer": {"claims": {}}}}
        with pytest.raises(UnauthorizedError):
            require_auth(event)
