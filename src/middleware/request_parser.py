"""Request parsing utilities for Lambda handlers."""

import json
from typing import Any

from src.middleware.error_handler import ValidationError


def parse_body(event: dict) -> dict:
    """Parse and return the JSON body from a Lambda event."""
    body = event.get("body")
    if not body:
        return {}
    if isinstance(body, dict):
        return body
    try:
        return json.loads(body)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValidationError("Invalid JSON in request body") from exc


def parse_path_params(event: dict) -> dict:
    """Extract path parameters from a Lambda event."""
    return event.get("pathParameters") or {}


def parse_query_params(event: dict) -> dict:
    """Extract query string parameters from a Lambda event."""
    return event.get("queryStringParameters") or {}


def get_user_id(event: dict) -> str | None:
    """Extract the Cognito user ID from the authorizer context."""
    request_context = event.get("requestContext", {})
    authorizer = request_context.get("authorizer", {})
    claims = authorizer.get("claims", {})
    return claims.get("sub")
