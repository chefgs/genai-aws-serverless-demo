import os
import textwrap
from typing import Any, Dict

import requests
import streamlit as st

API_URL = os.getenv("INCIDENT_HELPER_API_URL", "").strip()

st.set_page_config(
    page_title="Serverless GenAI Demo (Lambda + Bedrock)",
    page_icon="⚡",
    layout="centered",
)

st.title("⚡ Serverless GenAI Demo")
st.caption("From Prompt to Production-style Prototype • Streamlit → Lambda → Bedrock")

if not API_URL:
    st.error(
        "INCIDENT_HELPER_API_URL environment variable is not set.\n\n"
        "Set it to your Lambda Function URL or API Gateway endpoint before running."
    )
    st.stop()

with st.expander("🔧 Backend configuration (for you, not students)", expanded=False):
    st.write("Current backend URL:")
    st.code(API_URL, language="bash")

st.markdown(
    """
This prototype sends user-provided text to a **serverless backend** (AWS Lambda),  
which calls **Amazon Bedrock** to analyze it and returns structured output.

For the demo, we use an incident-style prompt, but this pattern works for any GenAI analysis or transformation.
"""
)

col1, col2 = st.columns(2)
with col1:
    incident_title = st.text_input("Title / short description", "Lambda 500 errors after new deploy")
with col2:
    service_context = st.text_input("Service / context", "AWS Lambda + API Gateway")

symptoms = st.text_area(
    "User-facing symptoms (what are you seeing?)",
    value=textwrap.dedent(
        """
API Gateway returns 500 errors for /generate endpoint.
Errors started after latest deployment.
Only some requests fail, others succeed.
"""
    ).strip(),
    height=120,
)

logs = st.text_area(
    "Text snippet to analyze (e.g., logs, code, config)",
    value=textwrap.dedent(
        """
2024-09-12T10:22:31.123Z ERROR InvokeError: TimeoutError talking to Bedrock
2024-09-12T10:22:31.123Z REQUEST_ID abc-123 Lambda timed out after 15 seconds
2024-09-12T10:22:45.987Z WARN Upstream model latency is high (over 10s)
"""
    ).strip(),
    height=150,
)

if st.button("🔍 Analyze with GenAI", type="primary"):
    if not symptoms.strip() and not logs.strip():
        st.warning("Please provide some text (symptoms and/or logs) to analyze.")
        st.stop()

    payload: Dict[str, Any] = {
        "incident_title": incident_title,
        "service_context": service_context,
        "symptoms": symptoms,
        "logs": logs,
    }

    with st.spinner("Calling serverless backend (Lambda + Bedrock)…"):
        try:
            resp = requests.post(API_URL, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            st.error(f"Error calling backend: {e}")
            st.stop()

    st.subheader("🧠 AI Analysis")
    summary = data.get("summary")
    hypotheses = data.get("hypotheses", [])
    checks = data.get("checks", [])
    fixes = data.get("fixes", [])

    if summary:
        st.markdown(f"**Summary:** {summary}")

    if hypotheses:
        st.markdown("### 🧩 Possible Root Causes (or key factors)")
        for i, h in enumerate(hypotheses, 1):
            st.markdown(f"**{i}. {h}**")

    if checks:
        st.markdown("### 🔎 What to Check / Do Next")
        for c in checks:
            st.markdown(f"- {c}")

    if fixes:
        st.markdown("### 🛠 Suggested Fixes (if applicable)")
        for f in fixes:
            st.markdown(f"- {f}")

    with st.expander("Raw backend response (for debugging / devs)", expanded=False):
        st.json(data)

