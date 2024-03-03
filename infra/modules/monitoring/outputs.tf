output "sns_topic_arn" {
  description = "SNS topic ARN for alarm notifications"
  value       = aws_sns_topic.alarms.arn
}

output "log_group_names" {
  description = "List of CloudWatch log group names for Lambda functions"
  value       = [for lg in aws_cloudwatch_log_group.lambda : lg.name]
}
