# Serverless GenAI Demo – Streamlit + AWS Lambda + Amazon Bedrock + Terraform

This bundle contains:

- **Backend:** AWS Lambda (Python) calling Amazon Bedrock
- **Frontend:** Streamlit app (Python)
- **Infra:** Terraform with a reusable Lambda module

Flow:

> Streamlit UI → HTTPS → Lambda → Bedrock → Lambda → JSON → UI

See conversation text for detailed usage steps (Terraform deploy + Streamlit run).

