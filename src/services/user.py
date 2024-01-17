"""User business logic."""

from datetime import datetime, timezone

from botocore.exceptions import ClientError

from src.middleware.error_handler import NotFoundError, ValidationError
from src.models import user as user_model
from src.utils import logger


def _validate_user_profile(data: dict) -> None:
    if not data or not isinstance(data, dict):
        raise ValidationError("Invalid user profile data")


def get_or_create_user(user_id: str, cognito_profile: dict | None = None) -> dict:
    """Fetch an existing user or auto-create on first access."""
    user = user_model.get_by_id(user_id)
    if user:
        return user

    cognito_profile = cognito_profile or {}
    user = {
        "userId": user_id,
        "email": cognito_profile.get("email"),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "profile": {},
    }

    try:
        user_model.create(user)
        logger.log("info", "UserCreated", user_id=user_id, outcome="success")
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return user_model.get_by_id(user_id)
        raise

    return user


def get_user(user_id: str) -> dict:
    """Fetch a user by ID."""
    user = user_model.get_by_id(user_id)
    if not user:
        raise NotFoundError(f"User not found: {user_id}")
    return user


def update_user_profile(user_id: str, updates: dict) -> dict:
    """Update a user's profile."""
    _validate_user_profile(updates)
    user = get_user(user_id)
    merged_profile = {**(user.get("profile") or {}), **updates}
    return user_model.update(
        user_id,
        {
            "profile": merged_profile,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        },
    )
