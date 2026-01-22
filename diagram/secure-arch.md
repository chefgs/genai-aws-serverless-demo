# Secure Architecture for Serverless GenAI


## Entry & Security

User hits API Gateway via HTTPS.

WAF in front for basic protection (rate limiting, IP block, basic rules).

API Gateway uses Cognito for JWT-based auth (only authenticated clients can access).

## Network Isolation

Lambda runs inside a private subnet in a VPC.

No direct internet exposure for the function.

## Model Access

Lambda uses a VPC endpoint to reach Amazon Bedrock (private path).

Bedrock is shown with a “Guardrails / Safety” block:

Bedrock Guardrails (policies for prompt/response filtering, PII, etc).

You decide rules; platform enforces them.

## Secrets & IAM

Lambda uses Secrets Manager for configs / secrets.

IAM role has minimal permissions:

bedrock:InvokeModel (and logs)

CloudWatch access for logging

## Ops

Lambda streams logs + metrics to CloudWatch.

Terraform provisions everything: API Gateway, WAF, Cognito, Lambda, VPC, endpoint, IAM, Secrets, logs.