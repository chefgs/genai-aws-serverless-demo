import json
import sys
from io import BytesIO
from pathlib import Path

from botocore.response import StreamingBody
from botocore.stub import ANY, Stubber

# Make the lambda module importable when running pytest from repo root.
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "lambda"))

import lambda_function  # noqa: E402  pylint: disable=wrong-import-position


def _make_streaming_body(payload: dict) -> StreamingBody:
    data = json.dumps(payload).encode()
    return StreamingBody(BytesIO(data), len(data))


def test_lambda_handler_parses_bedrock_response():
    response_payload = {
        "content": [
            {
                "text": "Summary line\n\n"
                "Possible root causes:\n- rc1\n"
                "Checks and suggested actions:\n- check1"
            }
        ]
    }

    with Stubber(lambda_function.bedrock) as stub:
        stub.add_response(
            "invoke_model",
            {
                "body": _make_streaming_body(response_payload),
                "contentType": "application/json",
            },
            {
                "modelId": lambda_function.BEDROCK_MODEL_ID,
                "contentType": "application/json",
                "accept": "application/json",
                "body": ANY,
            },
        )

        event = {
            "body": json.dumps(
                {
                    "incident_title": "t",
                    "service_context": "svc",
                    "symptoms": "a",
                    "logs": "b",
                }
            )
        }

        resp = lambda_function.lambda_handler(event, None)

    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["summary"].startswith("Summary line")
    assert body["hypotheses"] == ["rc1"]
    assert body["checks"] == ["check1"]
