variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "lambda_functions" {
  type = map(object({
    function_name = string
    arn           = string
    invoke_arn    = string
  }))
}
