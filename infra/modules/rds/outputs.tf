output "db_host" {
  description = "RDS MySQL endpoint hostname"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "RDS MySQL port"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "db_user" {
  description = "Database master username"
  value       = aws_db_instance.main.username
}

output "db_password" {
  description = "Database master password"
  value       = random_password.db.result
  sensitive   = true
}

output "lambda_security_group_id" {
  description = "Security group ID to attach to Lambda functions"
  value       = aws_security_group.lambda.id
}

output "subnet_ids" {
  description = "Private subnet IDs for Lambda VPC config"
  value       = aws_subnet.private[*].id
}
