# Lambda URL 403 Forbidden Troubleshooting Guide

## Problem
You received a 403 Forbidden error when accessing your AWS Lambda function URL.

## Analysis Steps
1. **Terraform Lambda Setup Review**
   - Checked `main.tf` and module code for Lambda function and URL configuration.
   - Verified `authorization_type = "NONE"` for public access.
   - Found no `aws_lambda_permission` resource for public invocation.

2. **IAM Role/Policy Review**
   - Lambda execution role only allows logging and Bedrock model invocation.
   - No effect on public invocation permissions.

3. **Permission Resource Missing**
   - Lambda URL requires explicit permission for public invocation via `aws_lambda_permission`.
   - Without this, AWS blocks public access, resulting in 403 errors.

## Solution
Added the following resource to `infra/modules/lambda_backend/main.tf`:

```hcl
resource "aws_lambda_permission" "allow_public_invoke" {
  statement_id  = "AllowPublicInvoke"
  action        = "lambda:InvokeFunctionUrl"
  function_name = aws_lambda_function.this.function_name
  principal     = "*"
  function_url_auth_type = "NONE"
}
```

## Debugging Steps
1. **Check Lambda URL Configuration**
   - Ensure `authorization_type = "NONE"` for public access.
2. **Verify Lambda Permission Resource**
   - Confirm `aws_lambda_permission` exists and allows public invoke.
3. **Apply Terraform Changes**
   - Run `terraform plan` and `terraform apply` to update resources.
4. **Test Lambda URL**
   - Access the Lambda URL in browser or via curl/Postman.
   - If using IAM auth, ensure your credentials have `lambda:InvokeFunctionUrl` permission.
5. **Check CloudWatch Logs**
   - Review logs for any Lambda execution errors.
6. **Review IAM Policies**
   - If using IAM authentication, verify caller permissions.

## Common Issues
- Missing `aws_lambda_permission` for public invoke.
- Incorrect `authorization_type`.
- IAM user/role lacks required permissions.
- Lambda URL not deployed or mismatched.

## References
- [AWS Lambda Function URLs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html)
- [Terraform AWS Lambda Permission](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission)

---

**After applying the fix, your Lambda URL should be accessible without 403 errors.**
