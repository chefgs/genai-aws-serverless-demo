# Serverless GenAI Demo – Streamlit + AWS Lambda + Amazon Bedrock + Terraform

This bundle contains:

- **Backend:** AWS Lambda (Python) calling Amazon Bedrock
- **Frontend:** Streamlit app (Python)
- **Infra:** Terraform with a reusable Lambda module

Flow:

> Streamlit UI → HTTPS → Lambda → Bedrock → Lambda → JSON → UI

See conversation text for detailed usage steps (Terraform deploy + Streamlit run).

## Model selection

- The Lambda uses environment variables to pick the Bedrock model and region:
  - `BEDROCK_MODEL_ID` (default: `anthropic.claude-3-haiku-20240307-v1:0`)
  - `BEDROCK_REGION` (default: `us-east-1`)
- For production, you can point to a stronger reasoning model. Example:  
  `BEDROCK_MODEL_ID=amazon.nova-pro-v1:0` (Nova 2). Keep the default as a lightweight fallback if the prod model is unavailable.

## Local testing (unit + mock demo)

- Install test deps (from repo root):  
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install boto3 botocore pytest
  ```
- Lambda unit test with Bedrock stub (no AWS):  
  ```bash
  pytest tests/test_lambda_local.py -q
  ```
- Optional real Bedrock integration (requires creds + access):  
  ```bash
  RUN_BEDROCK_INTEGRATION=1 pytest tests/test_lambda_bedrock_integration.py -q
  ```
- Mock backend for UI demo (no AWS):  
  ```bash
  python frontend/mock_backend.py  # starts http://localhost:9000
  # New shell:
  cd frontend && pip install -r requirements.txt
  INCIDENT_HELPER_API_URL=http://localhost:9000 streamlit run streamlit_app.py
  ```
