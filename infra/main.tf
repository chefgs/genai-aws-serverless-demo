provider "aws" {
  region = var.aws_region
}

locals {
  common_tags = {
    Project = var.project_name
    Stack   = "demo"
  }
}

module "lambda_backend" {
  source = "./modules/lambda_backend"

  function_name = "${var.project_name}-backend"
  runtime       = "python3.11"
  handler       = "lambda_function.lambda_handler"

  memory_size = 512
  timeout     = 30

  source_file = "${path.root}/../lambda/lambda_function.py"

  bedrock_region   = var.bedrock_region
  bedrock_model_id = var.bedrock_model_id

  enable_function_url = true

  tags = local.common_tags
}

