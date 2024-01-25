"""Auth middleware.

In this architecture, API Gateway Cognito Authorizer validates the token.
We only extract the userId from the authorizer context and trust it.
Do not reimplement auth logic in Lambda.
"""

from src.middleware.error_handler import UnauthorizedError
from src.middleware.request_parser import get_user_id


def require_auth(event: dict) -> str:
    """Require a valid authenticated user and return the userId."""
    user_id = get_user_id(event)
    if not user_id:
        raise UnauthorizedError("Missing or invalid authentication")
    return user_id
