"""POST /pain-reports — Create a new pain report."""

from src.middleware.auth import require_auth
from src.middleware.lambda_wrapper import wrap_handler
from src.middleware.request_parser import parse_body
from src.services.pain_report import create_pain_report
from src.utils.response_builder import success


def _handler(event, context):
    user_id = require_auth(event)
    body = parse_body(event)
    report = create_pain_report(user_id, body)
    return success(report, 201)


handler = wrap_handler(_handler, "createPainReport")
