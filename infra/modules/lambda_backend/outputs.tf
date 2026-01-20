output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.this.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.this.arn
}

output "lambda_function_url" {
  description = "Lambda function URL (if enabled)"
  value       = try(aws_lambda_function_url.this[0].function_url, null)
}

