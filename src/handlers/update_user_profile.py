"""PUT /users/me — Update current user profile."""

from src.middleware.auth import require_auth
from src.middleware.lambda_wrapper import wrap_handler
from src.middleware.request_parser import parse_body
from src.services.user import update_user_profile
from src.utils.response_builder import success


def _handler(event, context):
    user_id = require_auth(event)
    body = parse_body(event)
    user = update_user_profile(user_id, body)
    return success(user)


handler = wrap_handler(_handler, "updateUserProfile")
