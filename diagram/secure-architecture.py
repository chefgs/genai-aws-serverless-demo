from diagrams import Diagram, Cluster, Edge

from diagrams.onprem.client import Client
from diagrams.onprem.iac import Terraform

from diagrams.aws.network import APIGateway, VPC, PrivateSubnet
from diagrams.aws.security import WAF, Cognito, IAM
from diagrams.aws.compute import Lambda
from diagrams.aws.ml import Sagemaker  # stand-in icon for Amazon Bedrock
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import SecretsManager
from diagrams.aws.network import PrivateEndpoint


with Diagram(
    "Secure Serverless GenAI Architecture on AWS",
    filename="serverless-genai-secure-architecture",
    show=False,
    direction="LR",
):
    # Client side
    user = Client("User / Frontend\n(Web / Mobile / Streamlit)")

    # IaC outside account boundary
    tf = Terraform("Terraform IaC\n(Modules for API, Lambda,\nVPC, Guardrails)")

    with Cluster("AWS Account"):
        # Security and entry
        waf = WAF("AWS WAF\n(Edge Protection)")
        api_gw = APIGateway("Amazon API Gateway\n(HTTPS, Auth, Throttling)")
        auth = Cognito("Amazon Cognito\n(User Pool / JWT Auth)")

        with Cluster("VPC (Private App Network)"):
            private_subnet = PrivateSubnet("Private Subnet")

            with Cluster("Serverless GenAI Backend"):
                lambda_fn = Lambda("GenAI Backend\nAWS Lambda (Python)")

            # VPC endpoint to Bedrock (using generic PrivateEndpoint icon)
            bedrock_ep = PrivateEndpoint("VPC Endpoint\nfor Amazon Bedrock")
            bedrock = Sagemaker("Amazon Bedrock\n(Models + Guardrails)")

        # Ops & Security
        cw_logs = Cloudwatch("CloudWatch\nLogs & Metrics")
        iam_role = IAM("IAM Role\nLeast Privilege\n+ bedrock:InvokeModel")
        secrets = SecretsManager("Secrets Manager\nAPI keys, config")

    # Flows

    # User → WAF → API Gateway
    user >> Edge(label="HTTPS\nJSON (GenAI request)") >> waf >> api_gw

    # API Gateway → Lambda (private)
    api_gw >> Edge(label="Invoke (JWT-validated)\n+ path, headers, body") >> lambda_fn

    # Cognito used by API Gateway Authorizer
    auth >> Edge(label="JWT / Authorizer") >> api_gw

    # Lambda in private subnet
    lambda_fn - private_subnet

    # Lambda → Bedrock via VPC endpoint
    lambda_fn >> Edge(label="Converse / InvokeModel\n(secured via VPC endpoint)") >> bedrock_ep >> bedrock

    # Guardrails concept (logically in front of model)
    guardrails = WAF("Guardrails / Safety\n(Prompts & Responses Policies)")
    guardrails >> Edge(style="dotted", label="Policy config\n(Prompt filters,\nPII, safety) ") >> bedrock

    # Lambda → Observability & Secrets
    lambda_fn >> Edge(label="logs, metrics") >> cw_logs
    lambda_fn << Edge(label="read\nmodel IDs, config") << secrets

    # IAM role attached to Lambda
    iam_role - lambda_fn

    # Terraform provisions everything
    tf >> Edge(label="provisions\nAPI, WAF, Lambda,\nVPC, Endpoint, IAM") >> api_gw
    tf >> lambda_fn
    tf >> waf
    tf >> bedrock_ep
    tf >> iam_role
    tf >> secrets
    tf >> cw_logs
