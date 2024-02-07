"""Tests for src.services.notification."""

from unittest.mock import patch

import pytest

from src.services.notification import notify_auth_failure, notify_lambda_error, publish_metric


class TestPublishMetric:
    @patch("src.services.notification._cw_client")
    def test_success(self, mock_cw):
        publish_metric("TestMetric", 1.0)
        mock_cw.put_metric_data.assert_called_once()

    @patch("src.services.notification._cw_client")
    def test_failure_swallowed(self, mock_cw):
        from botocore.exceptions import ClientError

        mock_cw.put_metric_data.side_effect = ClientError({}, "PutMetricData")
        publish_metric("TestMetric", 1.0)  # should not raise


class TestNotifyAuthFailure:
    @patch("src.services.notification.publish_metric")
    def test_calls_publish(self, mock_publish):
        notify_auth_failure("u1", "expired")
        mock_publish.assert_called_once()


class TestNotifyLambdaError:
    @patch("src.services.notification.publish_metric")
    def test_calls_publish(self, mock_publish):
        notify_lambda_error("fn1", RuntimeError("oops"))
        mock_publish.assert_called_once()
