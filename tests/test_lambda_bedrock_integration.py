"""
Integration test that hits the real Amazon Bedrock endpoint.

Not run by default: set RUN_BEDROCK_INTEGRATION=1 and ensure AWS credentials
have bedrock:InvokeModel permissions for the chosen region/model.
"""

import json
import os

import boto3
import pytest

import lambda_function


skip_reason = "set RUN_BEDROCK_INTEGRATION=1 with AWS creds to call Bedrock"


@pytest.mark.skipif(not os.getenv("RUN_BEDROCK_INTEGRATION"), reason=skip_reason)
def test_lambda_handler_hits_real_bedrock():
    session = boto3.Session()
    if session.get_credentials() is None:
        pytest.skip("AWS credentials not configured for integration test")

    payload = {
        "incident_title": "Integration test",
        "service_context": "Lambda + Bedrock",
        "symptoms": "High latency reported",
        "logs": "Example log line",
    }

    event = {"body": json.dumps(payload)}
    resp = lambda_function.lambda_handler(event, None)

    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    # Content will vary; just assert the keys we expect.
    for key in ("summary", "hypotheses", "checks", "raw_text"):
        assert key in body
