## Deploying the Lambda (Bedrock-backed) 

These steps assume you only need the Lambda + HTTPS endpoint. For full infra as code, use the Terraform under `infra/`.

### Prereqs
- AWS CLI configured (`aws configure`) with permissions to create IAM roles, Lambdas, and (optionally) Function URLs or API Gateway.
- Bedrock access in the chosen region for your model ID.

### 1) Package the function
From repo root:
```bash
cd lambda
zip ../lambda.zip lambda_function.py
cd ..
```
The handler has no extra dependencies beyond the Lambda runtime’s `boto3`.

### 2) Create an execution role (one-time)
- Trust policy: Lambda.
- Policies: `AWSLambdaBasicExecutionRole` (logs) + `bedrock:InvokeModel` on the models you need. If you’re in a VPC, add VPC access role policy.

### 3) Create or update the function
Example create:
```bash
aws lambda create-function \
  --function-name incident-helper \
  --runtime python3.12 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::<acct>:role/<your-lambda-role> \
  --zip-file fileb://lambda.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment "Variables={BEDROCK_REGION=us-east-1,BEDROCK_MODEL_ID=amazon.nova-pro-v1:0,BEDROCK_MODEL_FALLBACK_ID=anthropic.claude-3-haiku-20240307-v1:0}"
```
Update code later with:
```bash
aws lambda update-function-code --function-name incident-helper --zip-file fileb://lambda.zip
```

### 4) Expose HTTPS
- Easiest: Lambda Function URL with `--auth-type NONE` for demo (or configure auth if needed).
  ```bash
  aws lambda create-function-url-config \
    --function-name incident-helper \
    --auth-type NONE \
    --cors "AllowOrigins=['*'],AllowMethods=['POST'],AllowHeaders=['*']"
  ```
- Or wire up API Gateway to the function and use its invoke URL.

### 5) Smoke test
Direct invoke:
```bash
aws lambda invoke \
  --function-name incident-helper \
  --payload '{"incident_title":"demo","service_context":"lambda"}' \
  out.json && cat out.json
```
Over HTTP (Function URL / API Gateway):
```bash
curl -X POST "<function-or-api-url>" \
  -H "Content-Type: application/json" \
  -d '{"incident_title":"demo","service_context":"lambda"}'
```

### 6) Hook up Streamlit
Run locally and point to the live endpoint:
```bash
INCIDENT_HELPER_API_URL=<function-or-api-url> streamlit run frontend/streamlit_app.py
```

### Notes
- Model selection via env vars: `BEDROCK_MODEL_ID` (default Nova 2) and `BEDROCK_MODEL_FALLBACK_ID` (default Haiku). Adjust to the models your account/region supports.
- Keep auth open (`NONE`) only for demos; restrict with IAM/auth if exposing publicly.
