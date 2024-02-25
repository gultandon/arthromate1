variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "log_level" {
  type = string
}

variable "runtime" {
  type = string
}

variable "db_host" {
  type = string
}

variable "db_port" {
  type = number
}

variable "db_name" {
  type = string
}

variable "db_user" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "subnet_ids" {
  type = list(string)
}

variable "lambda_security_group_ids" {
  type = list(string)
}

variable "cognito_user_pool_id" {
  type = string
}

variable "cognito_client_id" {
  type = string
}
