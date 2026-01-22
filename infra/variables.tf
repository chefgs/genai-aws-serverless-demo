variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-west-1"
}

variable "project_name" {
  description = "Project / stack name prefix"
  type        = string
  default     = "genai-serverless-demo"
}

variable "bedrock_region" {
  description = "Region where Amazon Bedrock is available"
  type        = string
  default     = "us-west-1"
}

variable "bedrock_model_id" {
  description = "Amazon Bedrock model ID to use"
  type        = string
  default     = "amazon.nova-2-sonic-v1:0"
}

