"""Pain Report business logic.

Handles validation, creation, retrieval, and deletion of pain reports.
"""

import time
import uuid
from datetime import datetime, timezone

from src.middleware.error_handler import NotFoundError, ValidationError
from src.models import pain_report as pain_report_model
from src.utils import logger

_VALID_JOINTS = {
    "left_knee",
    "right_knee",
    "left_hip",
    "right_hip",
    "left_shoulder",
    "right_shoulder",
    "left_wrist",
    "right_wrist",
    "left_ankle",
    "right_ankle",
    "left_elbow",
    "right_elbow",
    "spine",
    "neck",
    "jaw",
}

_VALID_MOBILITY = {"low", "medium", "high"}


def _validate_pain_report(data: dict) -> None:
    pain_level = data.get("painLevel")
    if not isinstance(pain_level, int) or pain_level < 0 or pain_level > 10:
        raise ValidationError("painLevel must be a number between 0 and 10")

    affected_joints = data.get("affectedJoints")
    if not isinstance(affected_joints, list) or len(affected_joints) == 0:
        raise ValidationError("affectedJoints must be a non-empty array")

    invalid_joints = [j for j in affected_joints if j not in _VALID_JOINTS]
    if invalid_joints:
        raise ValidationError(f"Invalid joints: {', '.join(invalid_joints)}")

    mobility = data.get("mobility")
    if mobility and mobility not in _VALID_MOBILITY:
        raise ValidationError(f"mobility must be one of: {', '.join(_VALID_MOBILITY)}")

    notes = data.get("notes")
    if notes is not None and not isinstance(notes, str):
        raise ValidationError("notes must be a string")
    if notes and len(notes) > 1000:
        raise ValidationError("notes must not exceed 1000 characters")


def create_pain_report(user_id: str, data: dict) -> dict:
    """Create a new pain report after validation."""
    start_time = time.time()
    _validate_pain_report(data)

    report = {
        "reportId": str(uuid.uuid4()),
        "userId": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "painLevel": data["painLevel"],
        "affectedJoints": data["affectedJoints"],
        "notes": data.get("notes"),
        "mobility": data.get("mobility"),
    }

    pain_report_model.create(report)

    duration_ms = int((time.time() - start_time) * 1000)
    logger.log(
        "info",
        "PainReportProcessed",
        user_id=user_id,
        request_id=report["reportId"],
        duration_ms=duration_ms,
        outcome="success",
    )

    return report


def get_pain_report(user_id: str, report_id: str) -> dict:
    """Fetch a single pain report."""
    report = pain_report_model.get_by_id(report_id, user_id)
    if not report:
        raise NotFoundError(f"Pain report not found: {report_id}")
    return report


def list_pain_reports(user_id: str, options: dict | None = None) -> list[dict]:
    """List pain reports for a user."""
    return pain_report_model.list_by_user(user_id, options or {})


def delete_pain_report(user_id: str, report_id: str) -> dict:
    """Delete a pain report."""
    report = pain_report_model.remove(report_id, user_id)
    if not report:
        raise NotFoundError(f"Pain report not found: {report_id}")
    return report
