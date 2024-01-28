"""GET /pain-reports — List pain reports for the authenticated user."""

from src.middleware.auth import require_auth
from src.middleware.lambda_wrapper import wrap_handler
from src.middleware.request_parser import parse_query_params
from src.services.pain_report import list_pain_reports
from src.utils.response_builder import success


def _handler(event, context):
    user_id = require_auth(event)
    query = parse_query_params(event)

    options = {
        "startDate": query.get("startDate"),
        "endDate": query.get("endDate"),
        "limit": int(query["limit"]) if query.get("limit") else 50,
    }

    reports = list_pain_reports(user_id, options)
    return success({"reports": reports, "count": len(reports)})


handler = wrap_handler(_handler, "listPainReports")
