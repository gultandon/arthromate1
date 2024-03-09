output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = module.api_gateway.api_url
}

output "rds_endpoint" {
  description = "RDS MySQL endpoint"
  value       = "${module.rds.db_host}:${module.rds.db_port}"
}

output "user_pool_id" {
  description = "Cognito User Pool ID"
  value       = module.cognito.user_pool_id
}

output "app_client_id" {
  description = "Cognito App Client ID"
  value       = module.cognito.app_client_id
}

output "sns_alarm_topic_arn" {
  description = "SNS topic ARN for CloudWatch alarms"
  value       = module.monitoring.sns_topic_arn
}
