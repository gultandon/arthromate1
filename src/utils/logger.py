"""Structured JSON logger for Lambda functions."""

import json
import logging
import os
from datetime import datetime, timezone

_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
}


def _get_log_level() -> int:
    raw = os.environ.get("LOG_LEVEL", "info").lower()
    return _LOG_LEVELS.get(raw, logging.INFO)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            payload.update(record.extra)
        return json.dumps(payload, default=str)


_handler = logging.StreamHandler()
_handler.setFormatter(_JsonFormatter())

logger = logging.getLogger("arthromate")
logger.setLevel(_get_log_level())
logger.handlers = [_handler]
logger.propagate = False


def log(level: str, message: str, **kwargs) -> None:
    """Emit a structured log entry."""
    level_int = _LOG_LEVELS.get(level, logging.INFO)
    if level_int < logger.level:
        return
    record = logger.makeRecord(
        logger.name,
        level_int,
        "(unknown file)",
        0,
        message,
        (),
        None,
    )
    record.extra = kwargs
    logger.handle(record)
