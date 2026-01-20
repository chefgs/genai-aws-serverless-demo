import json
import os
import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def build_prompt(payload: Dict[str, Any]) -> str:
    """Builds a natural language prompt for the LLM based on user input."""
    incident_title = payload.get("incident_title", "Unknown incident")
    service_context = payload.get("service_context", "Unknown service")
    symptoms = payload.get("symptoms", "").strip()
    logs = payload.get("logs", "").strip()

    prompt = f"""You are a senior cloud and DevOps engineer.
You help analyze issues in AWS-based systems (Lambda, API Gateway, Bedrock, etc.).

Analyze the following situation and respond briefly but practically.

Incident title: {incident_title}
Service context: {service_context}

Symptoms:
{symptoms or "N/A"}

Logs:
{logs or "N/A"}

Return your answer in three sections with clear bullet points:

1. Summary (1–2 sentences)
2. Possible root causes (3–5 bullets)
3. Checks and suggested actions (5–8 bullets)

Focus on actionable, realistic steps (CloudWatch, timeouts, retries, IAM, network, configuration issues, etc.).
Avoid inventing internal company details or sensitive information.
"""
    return prompt


def call_bedrock_model(prompt: str) -> str:
    """Calls the configured Bedrock model (e.g., Claude 3 Haiku) with a simple chat-style request."""
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ],
                }
            ],
        }
    )

    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        response_body = json.loads(response.get("body").read())
        text = response_body["content"][0]["text"]
        return text
    except ClientError as e:
        logger.error(f"Error invoking Bedrock model: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling Bedrock: {e}")
        raise


def parse_ai_response(text: str) -> Dict[str, Any]:
    """Naive parser that splits the LLM response into sections."""
    sections = {"summary": "", "hypotheses": [], "checks": [], "fixes": []}

    current = "summary"
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for line in lines:
        l = line.lower()
        if "possible root cause" in l or "possible root causes" in l or "root causes" in l:
            current = "hypotheses"
            continue
        if "checks and suggested actions" in l or "checks / actions" in l or "what to check" in l:
            current = "checks"
            continue

        if current in ("hypotheses", "checks", "fixes") and (
            line.startswith("-") or line.startswith("•") or line.startswith("*")
        ):
            item = line.lstrip("-•* ").strip()
            if current == "checks":
                sections["checks"].append(item)
            elif current == "hypotheses":
                sections["hypotheses"].append(item)
            else:
                sections["fixes"].append(item)
        else:
            if current == "summary":
                if sections["summary"]:
                    sections["summary"] += " " + line
                else:
                    sections["summary"] = line

    if not sections["summary"]:
        sections["summary"] = text[:300]

    return sections


def lambda_handler(event, context):
    logger.info(f"Incoming event: {json.dumps(event)[:500]}")

    try:
        if "body" in event:
            body = event["body"]
            if isinstance(body, str):
                payload = json.loads(body)
            else:
                payload = body
        else:
            payload = event
    except Exception as e:
        logger.error(f"Error parsing request body: {e}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON body"}),
        }

    try:
        prompt = build_prompt(payload)
        ai_text = call_bedrock_model(prompt)
        parsed = parse_ai_response(ai_text)

        response_body = {
            "summary": parsed.get("summary"),
            "hypotheses": parsed.get("hypotheses", []),
            "checks": parsed.get("checks", []),
            "fixes": parsed.get("fixes", []),
            "raw_text": ai_text,
        }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(response_body),
        }
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
        }

