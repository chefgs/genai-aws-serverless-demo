output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda_backend.lambda_function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.lambda_backend.lambda_function_arn
}

output "lambda_function_url" {
  description = "Public URL for the Lambda function (if enabled)"
  value       = module.lambda_backend.lambda_function_url
}

