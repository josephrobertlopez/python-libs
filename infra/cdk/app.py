#!/usr/bin/env python3

import os
from aws_cdk import App, Environment
from dotenv import load_dotenv

from stacks.artifact_stack import ArtifactStack
from stacks.pipeline_stack import CodePipelineStack

# Load environment variables
load_dotenv()

# Initialize the CDK app
app = App()

# Define environment variables or use defaults
env_name = os.getenv("ENVIRONMENT", "dev")
project_name = os.getenv("PROJECT_NAME", "python-libs")

# Define the AWS environment (account and region)
aws_env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT", "000000000000"),
    region=os.getenv("CDK_DEFAULT_REGION", "us-east-1")
)

# Create the artifact stack
artifact_stack = ArtifactStack(
    app,
    f"{project_name}-artifact-stack",
    env_name=env_name,
    project_name=project_name,
    env=aws_env,  # Pass the environment explicitly
)

# Create the CodePipeline stack (only if not in LocalStack mode)
pipeline_enabled = os.getenv("ENABLE_PIPELINE", "false").lower() == "true"
if pipeline_enabled:
    pipeline_stack = CodePipelineStack(
        app,
        f"{project_name}-pipeline-stack",
        artifact_bucket=artifact_stack.artifact_bucket,
        env_name=env_name,
        project_name=project_name,
        env=aws_env,
    )
    # Add dependency to ensure artifact bucket is created first
    pipeline_stack.add_dependency(artifact_stack)

# Add tags to all resources
app.node.add_metadata("project", project_name)
app.node.add_metadata("environment", env_name)

# Synthesize the CloudFormation template
app.synth()
