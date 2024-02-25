output "lambda_functions" {
  description = "Map of Lambda function metadata"
  value = {
    for name, fn in aws_lambda_function.functions : name => {
      function_name = fn.function_name
      arn           = fn.arn
      invoke_arn    = fn.invoke_arn
    }
  }
}

output "lambda_role_arn" {
  description = "IAM role ARN used by Lambda functions"
  value       = aws_iam_role.lambda_execution.arn
}
