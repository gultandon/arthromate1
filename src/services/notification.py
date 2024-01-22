"""Notification service.

Publishes CloudWatch custom metrics and handles notifications.
"""

import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from src.utils import logger

_REGION = os.environ.get("AWS_REGION", "ap-south-1")
_NAMESPACE = "ArthroMate/Backend"

_cw_client = boto3.client("cloudwatch", region_name=_REGION)


def publish_metric(
    metric_name: str,
    value: float,
    unit: str = "Count",
    dimensions: list[dict] | None = None,
) -> None:
    """Publish a custom CloudWatch metric."""
    dimensions = dimensions or []
    try:
        _cw_client.put_metric_data(
            Namespace=_NAMESPACE,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit,
                    "Timestamp": datetime.now(timezone.utc),
                    "Dimensions": dimensions,
                }
            ],
        )
        logger.log("debug", "Metric published", metric_name=metric_name, value=value, unit=unit)
    except ClientError as exc:
        logger.log(
            "error",
            "Failed to publish metric",
            metric_name=metric_name,
            error=str(exc),
        )


def notify_auth_failure(user_id: str | None, reason: str) -> None:
    """Record an authentication failure metric."""
    publish_metric(
        "AuthFailure",
        1,
        "Count",
        [{"Name": "Reason", "Value": reason}],
    )
    logger.log("warn", "AuthFailure", user_id=user_id, reason=reason)


def notify_lambda_error(function_name: str, error: Exception) -> None:
    """Record a Lambda error metric."""
    publish_metric(
        "LambdaError",
        1,
        "Count",
        [{"Name": "FunctionName", "Value": function_name}],
    )
    logger.log("error", "LambdaError", function_name=function_name, error=str(error))
