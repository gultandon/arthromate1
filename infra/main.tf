terraform {
  required_version = ">= 1.2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "rds" {
  source       = "./modules/rds"
  project_name = var.project_name
  environment  = var.environment
}

module "cognito" {
  source       = "./modules/cognito"
  project_name = var.project_name
  environment  = var.environment
}

module "lambda" {
  source       = "./modules/lambda"
  project_name = var.project_name
  environment  = var.environment
  log_level    = var.log_level
  runtime      = var.lambda_runtime

  db_host     = module.rds.db_host
  db_port     = module.rds.db_port
  db_name     = module.rds.db_name
  db_user     = module.rds.db_user
  db_password = module.rds.db_password

  subnet_ids                = module.rds.subnet_ids
  lambda_security_group_ids = [module.rds.lambda_security_group_id]

  cognito_user_pool_id = module.cognito.user_pool_id
  cognito_client_id    = module.cognito.app_client_id
}

module "api_gateway" {
  source       = "./modules/api_gateway"
  project_name = var.project_name
  environment  = var.environment

  lambda_functions      = module.lambda.lambda_functions
  cognito_user_pool_arn = module.cognito.user_pool_arn
}

module "monitoring" {
  source       = "./modules/monitoring"
  project_name = var.project_name
  environment  = var.environment

  lambda_functions = module.lambda.lambda_functions
}

module "cicd" {
  source       = "./modules/cicd"
  project_name = var.project_name
  environment  = var.environment

  github_owner          = var.github_owner
  github_repo           = var.github_repo
  github_branch         = var.github_branch
  github_connection_arn = var.github_connection_arn
}
