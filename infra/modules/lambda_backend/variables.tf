variable "function_name" {
  description = "Lambda function name"
  type        = string
}

variable "runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "handler" {
  description = "Lambda handler"
  type        = string
  default     = "lambda_function.lambda_handler"
}

variable "memory_size" {
  description = "Lambda memory size (MB)"
  type        = number
  default     = 512
}

variable "timeout" {
  description = "Lambda timeout (seconds)"
  type        = number
  default     = 30
}

variable "source_file" {
  description = "Path to lambda_function.py"
  type        = string
}

variable "bedrock_region" {
  description = "Region where Bedrock is used"
  type        = string
}

variable "bedrock_model_id" {
  description = "Bedrock model ID"
  type        = string
}

variable "enable_function_url" {
  description = "Whether to create a public Lambda Function URL (for demo)"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

