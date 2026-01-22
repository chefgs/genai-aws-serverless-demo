import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from textwrap import shorten


def synthesize_response(payload: dict) -> dict:
    """Builds a deterministic, payload-aware response without calling AWS."""
    title = payload.get("incident_title") or "Untitled incident"
    svc = payload.get("service_context") or "Unknown service"
    symptoms = payload.get("symptoms") or ""
    logs = payload.get("logs") or ""

    summary = f"{title} affecting {svc}"
    if symptoms:
        summary += f"; symptoms: {shorten(symptoms, width=120, placeholder='…')}"

    hypotheses = [
        f"Config or dependency issue in {svc}",
        "Timeouts or throttling under load",
        "Recent deploy introduced a breaking change",
    ]
    if "timeout" in logs.lower():
        hypotheses.insert(0, "Upstream model timeout or cold start delay")
    if "5" in logs:
        hypotheses.append("HTTP 5xx indicates backend instability")

    checks = [
        "Review recent deploy/config changes",
        "Check CloudWatch logs for stack traces and latency",
        "Confirm IAM permissions for Bedrock/model access",
        "Inspect retry and timeout settings in client/backend",
    ]
    if "api gateway" in svc.lower():
        checks.append("Verify API Gateway/Lambda integration latency and timeouts")

    fixes = [
        "Add retries/backoff around Bedrock calls",
        "Raise Lambda timeout or reduce model token usage",
        "Rollback suspect deploy if errors align with release window",
    ]

    return {
        "summary": payload.get("summary_override", summary),
        "hypotheses": payload.get("hypotheses_override", hypotheses),
        "checks": payload.get("checks_override", checks),
        "fixes": payload.get("fixes_override", fixes),
        "raw_text": payload.get("raw_text_override", f"Synthesized for {title} / {svc}"),
    }


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def log_message(self, format: str, *args):  # noqa: A003
        # Quieter test output; comment out to see access logs.
        return

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length else b"{}"

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(b'{"error": "Invalid JSON"}')
            return

        response = synthesize_response(payload)

        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode())


def run():
    port = int(os.environ.get("MOCK_BACKEND_PORT", "9000"))
    server = HTTPServer(("", port), Handler)
    print(f"Mock backend listening on http://localhost:{port} (Ctrl+C to stop)")
    server.serve_forever()


if __name__ == "__main__":
    run()
