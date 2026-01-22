from diagrams import Diagram, Cluster, Edge

from diagrams.onprem.client import Client
from diagrams.onprem.iac import Terraform

from diagrams.aws import network as aws_net
from diagrams.aws import security as aws_sec
from diagrams.aws import compute as aws_comp
from diagrams.aws import management as aws_mgmt
from diagrams.aws import ml as aws_ml


with Diagram(
    "Secure Serverless GenAI Architecture on AWS",
    filename="serverless-genai-secure-architecture",
    show=False,
    direction="LR",
):
    # Client / caller
    user = Client("User / Frontend\n(Web / Mobile / Streamlit)")

    # IaC
    tf = Terraform("Terraform IaC\n(API, Lambda,\nVPC, Guardrails)")

    with Cluster("AWS Account"):
        # Edge security & entry
        waf = aws_sec.WAF("AWS WAF\n(Edge Protection)")
        api_gw = aws_net.APIGateway("Amazon API Gateway\nHTTPS, Auth, Throttling")
        cognito = aws_sec.Cognito("Amazon Cognito\nJWT / User Pool")

        with Cluster("VPC (Private App Network)"):
            vpc = aws_net.VPC("VPC")
            private_subnet = aws_net.PrivateSubnet("Private Subnet")

            with Cluster("Serverless GenAI Backend"):
                lambda_fn = aws_comp.Lambda("GenAI Backend\nAWS Lambda (Python)")

            # VPC Endpoint to Bedrock
            bedrock_ep = aws_net.Endpoint("VPC Endpoint\nfor Amazon Bedrock")

            # Bedrock + Guardrails
            bedrock = aws_ml.Bedrock("Amazon Bedrock\n(Models)")
            guardrails = aws_sec.WAFFilteringRule("Guardrails / Safety\nPolicies")

        # Ops & security services
        cw_logs = aws_mgmt.Cloudwatch("CloudWatch\nLogs & Metrics")
        iam_role = aws_sec.IAM("IAM Role\nLeast Privilege")
        secrets = aws_sec.SecretsManager("Secrets Manager\nModel IDs, config")

    # === Flows ===

    # User → WAF → API Gateway
    user >> Edge(label="HTTPS\nJSON (GenAI request)") >> waf >> api_gw

    # Auth: Cognito as authorizer for API Gateway
    cognito >> Edge(label="JWT / Authorizer") >> api_gw

    # API Gateway → Lambda in VPC
    api_gw >> Edge(label="Invoke\nvalidated request") >> lambda_fn
    lambda_fn - private_subnet
    vpc - private_subnet

    # Lambda → Bedrock via VPC endpoint
    lambda_fn >> Edge(label="Converse / InvokeModel\n(private via VPC endpoint)") >> bedrock_ep >> bedrock

    # Guardrails conceptually in front of model
    guardrails >> Edge(
        style="dotted",
        label="Prompt / response\nsafety, PII filters,\npolicy checks",
    ) >> bedrock

    # Observability & secrets
    lambda_fn >> Edge(label="logs, metrics") >> cw_logs
    lambda_fn << Edge(label="read config,\nmodel IDs") << secrets

    # IAM attached to Lambda
    iam_role - lambda_fn

    # Terraform provisions infra
    tf >> Edge(label="provision\nAPI, WAF, Lambda,\nVPC, endpoint, IAM") >> api_gw
    tf >> lambda_fn
    tf >> waf
    tf >> bedrock_ep
    tf >> iam_role
    tf >> secrets
    tf >> cw_logs
