"""Tests for src.utils.logger."""

import json
import logging

import src.utils.logger


class _Capture(logging.Handler):
    """Capture log records for test assertions."""

    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


def _with_capture(test_fn):
    original_level = src.utils.logger.logger.level
    handler = _Capture()
    handler.setLevel(logging.DEBUG)
    src.utils.logger.logger.handlers.clear()
    src.utils.logger.logger.addHandler(handler)
    src.utils.logger.logger.setLevel(logging.DEBUG)
    try:
        test_fn(handler.records)
    finally:
        src.utils.logger.logger.handlers.clear()
        src.utils.logger.logger.setLevel(original_level)


class TestLogger:
    def test_json_output(self):
        def _test(records):
            src.utils.logger.log("info", "hello", user_id="u1")
            assert len(records) == 1
            payload = json.loads(src.utils.logger._JsonFormatter().format(records[0]))
            assert payload["level"] == "info"
            assert payload["message"] == "hello"
            assert payload["user_id"] == "u1"
            assert "timestamp" in payload

        _with_capture(_test)

    def test_respects_log_level(self):
        def _test(records):
            src.utils.logger.logger.setLevel(logging.WARNING)
            src.utils.logger.log("info", "should be ignored")
            src.utils.logger.log("warn", "should appear")
            assert len(records) == 1
            assert records[0].levelno == logging.WARNING

        _with_capture(_test)

    def test_debug_level(self):
        def _test(records):
            src.utils.logger.log("debug", "debug msg")
            assert len(records) == 1
            assert records[0].levelno == logging.DEBUG

        _with_capture(_test)
