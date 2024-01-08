"""Standard API response builder for Lambda functions."""


from typing import Any


def success(data: Any, status_code: int = 200) -> dict:
    """Build a successful API response envelope."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": {
            "success": True,
            "data": data,
            "error": None,
        },
    }


def error(message: str, status_code: int = 500, details: Any = None) -> dict:
    """Build an error API response envelope."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": {
            "success": False,
            "data": None,
            "error": {
                "message": message,
                "details": details,
            },
        },
    }
