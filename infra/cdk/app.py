#!/usr/bin/env python3

import os
from aws_cdk import App
from dotenv import load_dotenv

from stacks.artifact_stack import ArtifactStack

# Load environment variables
load_dotenv()

# Initialize the CDK app
app = App()

# Define environment variables or use defaults
env_name = os.getenv("ENVIRONMENT", "dev")
project_name = os.getenv("PROJECT_NAME", "python-libs")

# Create the artifact stack
artifact_stack = ArtifactStack(
    app,
    f"{project_name}-artifact-stack",
    env_name=env_name,
    project_name=project_name,
)

# Add tags to all resources
app.node.add_metadata("project", project_name)
app.node.add_metadata("environment", env_name)

# Synthesize the CloudFormation template
app.synth()
