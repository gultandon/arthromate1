data "aws_region" "current" {}

locals {
  lambda_names = toset([
    "createPainReport",
    "listPainReports",
    "getPainReport",
    "deletePainReport",
    "getUserProfile",
    "updateUserProfile",
  ])

  lambda_configs = {
    createPainReport = {
      description = "Create a new pain report"
      memory      = 256
      timeout     = 10
      handler     = "src.handlers.create_pain_report.handler"
    }
    listPainReports = {
      description = "List pain reports for a user"
      memory      = 256
      timeout     = 10
      handler     = "src.handlers.list_pain_reports.handler"
    }
    getPainReport = {
      description = "Get a single pain report"
      memory      = 256
      timeout     = 10
      handler     = "src.handlers.get_pain_report.handler"
    }
    deletePainReport = {
      description = "Delete a pain report"
      memory      = 256
      timeout     = 10
      handler     = "src.handlers.delete_pain_report.handler"
    }
    getUserProfile = {
      description = "Get user profile"
      memory      = 256
      timeout     = 10
      handler     = "src.handlers.get_user_profile.handler"
    }
    updateUserProfile = {
      description = "Update user profile"
      memory      = 256
      timeout     = 10
      handler     = "src.handlers.update_user_profile.handler"
    }
  }
}

resource "terraform_data" "zip_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/zips"
  }
}

data "archive_file" "lambda_zip" {
  depends_on = [terraform_data.zip_dir]

  type        = "zip"
  source_dir  = "${path.root}/../src"
  output_path = "${path.module}/zips/lambda.zip"
}

resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Required for Lambda to create/manage ENIs when running inside a VPC
resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "lambda_cloudwatch" {
  name = "${var.project_name}-lambda-cloudwatch-policy-${var.environment}"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["cloudwatch:PutMetricData"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "functions" {
  for_each = local.lambda_configs

  function_name    = "${var.project_name}-${each.key}-${var.environment}"
  role             = aws_iam_role.lambda_execution.arn
  handler          = each.value.handler
  runtime          = var.runtime
  memory_size      = each.value.memory
  timeout          = each.value.timeout
  description      = each.value.description
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.lambda_security_group_ids
  }

  environment {
    variables = {
      DB_HOST              = var.db_host
      DB_PORT              = tostring(var.db_port)
      DB_NAME              = var.db_name
      DB_USER              = var.db_user
      DB_PASSWORD          = var.db_password
      COGNITO_USER_POOL_ID = var.cognito_user_pool_id
      COGNITO_CLIENT_ID    = var.cognito_client_id
      AWS_REGION           = data.aws_region.current.name
      LOG_LEVEL            = var.log_level
    }
  }

  tags = {
    Name        = each.key
    Environment = var.environment
  }
}

resource "aws_lambda_permission" "api_gateway" {
  for_each = aws_lambda_function.functions

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "apigateway.amazonaws.com"
}
