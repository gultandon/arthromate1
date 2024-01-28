"""DELETE /pain-reports/{reportId} — Delete a pain report."""

from src.middleware.auth import require_auth
from src.middleware.lambda_wrapper import wrap_handler
from src.middleware.request_parser import parse_path_params
from src.services.pain_report import delete_pain_report
from src.utils.response_builder import success


def _handler(event, context):
    user_id = require_auth(event)
    params = parse_path_params(event)
    report = delete_pain_report(user_id, params["reportId"])
    return success(report)


handler = wrap_handler(_handler, "deletePainReport")
