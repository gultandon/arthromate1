"""GET /users/me — Get current user profile."""

from src.middleware.auth import require_auth
from src.middleware.lambda_wrapper import wrap_handler
from src.services.user import get_user
from src.utils.response_builder import success


def _handler(event, context):
    user_id = require_auth(event)
    user = get_user(user_id)
    return success(user)


handler = wrap_handler(_handler, "getUserProfile")
