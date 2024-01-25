"""Lambda error middleware.

Wraps handlers to catch errors and format them consistently.
"""

import time
from typing import Any, Callable

from src.middleware.error_handler import AppError
from src.utils import logger
from src.utils.response_builder import error as build_error


def wrap_handler(handler: Callable, function_name: str) -> Callable:
    """Wrap a Lambda handler with error handling and logging."""

    def wrapper(event: dict, context: Any) -> dict:
        request_id = (
            getattr(context, "aws_request_id", None)
            or event.get("requestContext", {}).get("requestId")
            or "unknown"
        )
        start_time = time.time()

        try:
            logger.log(
                "debug",
                "Lambda invocation started",
                function_name=function_name,
                request_id=request_id,
                path=event.get("path"),
                http_method=event.get("httpMethod"),
            )

            result = handler(event, context)

            duration_ms = int((time.time() - start_time) * 1000)
            logger.log(
                "debug",
                "Lambda invocation completed",
                function_name=function_name,
                request_id=request_id,
                duration_ms=duration_ms,
                status_code=result.get("statusCode"),
            )
            return result
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.log(
                "error",
                "Lambda invocation failed",
                function_name=function_name,
                request_id=request_id,
                duration_ms=duration_ms,
                error=str(exc),
            )

            if isinstance(exc, AppError):
                return build_error(str(exc), exc.status_code, {"code": exc.code})

            return build_error(
                "Internal server error",
                500,
                {"code": "INTERNAL_ERROR", "request_id": request_id},
            )

    return wrapper
