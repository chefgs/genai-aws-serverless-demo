from diagrams import Diagram, Cluster, Edge

from diagrams.onprem.client import Client
from diagrams.onprem.iac import Terraform

from diagrams.aws.compute import Lambda
from diagrams.aws.ml import Sagemaker        # used as a Bedrock icon stand-in
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import IAM


with Diagram(
    "Serverless GenAI App on AWS",
    filename="serverless-genai-architecture",
    show=False,
    direction="LR",
):
    # Local / client side
    with Cluster("Client / Developer"):
        ui = Client("Streamlit Web UI\n(Local Dev Machine)")

    # AWS side
    with Cluster("AWS Account"):
        with Cluster("Serverless Backend"):
            lambda_fn = Lambda("GenAI Backend\nAWS Lambda (Python)")

        with Cluster("AI Services"):
            # Diagrams doesn't (yet) have a Bedrock icon; using SageMaker as a visual stand-in,
            # label clearly as Bedrock.
            bedrock = Sagemaker("Amazon Bedrock\n(Claude / Nova / Titan)")

        with Cluster("Ops & Security"):
            cw_logs = Cloudwatch("CloudWatch Logs\nLambda Logs & Metrics")
            iam_role = IAM("IAM Role\nbedrock:InvokeModel\n+ Logging")

    # IaC outside the account boundary (conceptually)
    tf = Terraform("Terraform IaC\ninfra/ + modules/\n(Terraform MCP friendly)")

    # Traffic flow: UI -> Lambda -> Bedrock -> Lambda -> UI
    ui >> Edge(
        label="HTTPS POST\nJSON payload\n(incident_title, service_context,\n symptoms, logs)"
    ) >> lambda_fn

    lambda_fn >> Edge(
        label="InvokeModel / Converse API\nprompt + context"
    ) >> bedrock

    bedrock >> Edge(
        label="LLM response\n(text: summary, bullets, checks)"
    ) >> lambda_fn

    lambda_fn >> Edge(
        label="Structured JSON\nsummary / hypotheses / checks / fixes"
    ) >> ui

    # Observability & security
    lambda_fn >> Edge(label="logs + metrics") >> cw_logs
    iam_role - lambda_fn

    # Terraform provisioning
    tf >> Edge(label="provisions\nLambda, IAM, Logs, Function URL") >> lambda_fn
    tf >> iam_role
    tf >> cw_logs
