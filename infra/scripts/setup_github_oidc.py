#!/usr/bin/env python3

"""
Setup GitHub OIDC Integration with AWS

This script helps create the necessary AWS resources for GitHub Actions to
use OpenID Connect (OIDC) to authenticate with AWS without long-lived credentials.

It will:
1. Create an IAM OIDC Identity Provider for GitHub Actions
2. Create an IAM Role with the necessary permissions for CDK deployment
3. Configure the trust policy to allow GitHub Actions to assume the role

Usage:
    python setup_github_oidc.py [OPTIONS]

Options:
    --repo TEXT           GitHub repository in format owner/repo  [required]
    --account-id TEXT     AWS Account ID  [required]
    --region TEXT         AWS Region (default: us-east-1)
    --role-name TEXT      Name for the IAM role (default: GitHubActionsCDKRole)
    --ref TEXT            Git reference to authorize (default: refs/heads/main)
    --help                Show this message and exit.
"""

import json
import subprocess
import sys
from pathlib import Path

import boto3
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


console = Console()


def run_command(command: str) -> str:
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        console.print(f"Error running command: {command}")
        console.print(f"Error message: {e.stderr}")
        sys.exit(1)


def get_github_oidc_thumbprint() -> str:
    """Get the thumbprint for GitHub's OIDC provider."""
    console.print("Retrieving GitHub OIDC provider thumbprint...")
    try:
        # Complex command to get the GitHub OIDC thumbprint
        cmd = (
            "curl -s https://token.actions.githubusercontent.com/.well-known/openid-configuration | "
            "jq -r '.jwks_uri' | xargs curl -s | jq -r '.keys[0].x5c[0]' | "
            "base64 -d | openssl x509 -fingerprint -noout | sed 's/.*=//' | tr -d ':' | tr '[:upper:]' '[:lower:]'"
        )
        return run_command(cmd)
    except Exception as e:
        console.print(f"Error getting thumbprint: {str(e)}")
        console.print("Please make sure you have jq, openssl, and curl installed.")
        sys.exit(1)


def create_oidc_provider(iam_client, thumbprint: str) -> str:
    """Create the IAM OIDC Identity Provider for GitHub Actions."""
    console.print("Creating IAM OIDC provider for GitHub Actions...")
    try:
        response = iam_client.create_open_id_connect_provider(
            Url="https://token.actions.githubusercontent.com",
            ClientIDList=["sts.amazonaws.com"],
            ThumbprintList=[thumbprint],
        )
        provider_arn = response["OpenIDConnectProviderArn"]
        console.print(f"OIDC provider created: {provider_arn}")
        return provider_arn
    except iam_client.exceptions.EntityAlreadyExistsException:
        console.print("OIDC provider already exists, retrieving ARN...")
        response = iam_client.list_open_id_connect_providers()
        for provider in response["OpenIDConnectProviderList"]:
            provider_arn = provider["Arn"]
            if "token.actions.githubusercontent.com" in provider_arn:
                console.print(f"Using existing OIDC provider: {provider_arn}")
                return provider_arn
        console.print("Could not find existing GitHub OIDC provider")
        sys.exit(1)
    except Exception as e:
        console.print(f"Error creating OIDC provider: {str(e)}")
        sys.exit(1)


def create_trust_policy(provider_arn: str, repo: str, ref: str) -> dict:
    """Create the trust policy for the IAM role."""
    console.print(f"Creating trust policy for repo {repo} and ref {ref}...")
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Federated": provider_arn},
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                        "token.actions.githubusercontent.com:sub": f"repo:{repo}:{ref}",
                    }
                },
            }
        ],
    }


def create_cdk_policy() -> dict:
    """Create the IAM policy for CDK deployment."""
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "cloudformation:*",
                    "s3:*",
                    "iam:PassRole",
                    "iam:GetRole",
                    "iam:CreateRole",
                    "iam:AttachRolePolicy",
                    "iam:PutRolePolicy",
                    "ssm:GetParameter",
                    "codecommit:*",
                    "codepipeline:*",
                    "codebuild:*",
                ],
                "Resource": "*",
            }
        ],
    }


def create_iam_role(iam_client, role_name: str, trust_policy: dict) -> str:
    """Create the IAM role with the trust policy."""
    console.print(f"Creating IAM role {role_name}...")
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for GitHub Actions OIDC authentication for CDK deployment",
        )
        role_arn = response["Role"]["Arn"]
        console.print(f"IAM role created: {role_arn}")
        return role_arn
    except iam_client.exceptions.EntityAlreadyExistsException:
        console.print(f"Role {role_name} already exists, updating trust policy...")
        iam_client.update_assume_role_policy(
            RoleName=role_name, PolicyDocument=json.dumps(trust_policy)
        )
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response["Role"]["Arn"]
        console.print(f"Using existing role: {role_arn}")
        return role_arn
    except Exception as e:
        console.print(f"Error creating IAM role: {str(e)}")
        sys.exit(1)


def attach_inline_policy(iam_client, role_name: str, policy: dict) -> None:
    """Attach an inline policy to the IAM role."""
    console.print(f"Attaching inline policy to role {role_name}...")
    try:
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName="CDKDeploymentPolicy",
            PolicyDocument=json.dumps(policy),
        )
        console.print("Inline policy attached successfully")
    except Exception as e:
        console.print(f"Error attaching inline policy: {str(e)}")
        sys.exit(1)


def generate_github_secret_instructions(role_arn: str) -> None:
    """Generate instructions for setting up GitHub secrets."""
    instructions = Text()
    instructions.append("\n1. Go to your GitHub repository's Settings > Secrets and variables > Actions\n")
    instructions.append("2. Click on 'New repository secret'\n")
    instructions.append("3. Add the following secret:\n\n")
    instructions.append("   Name: AWS_ROLE_TO_ASSUME\n")
    instructions.append(f"   Value: {role_arn}\n\n")
    instructions.append("4. If you want to enable the CodePipeline deployment:\n")
    instructions.append("   - Go to 'Variables' tab\n")
    instructions.append("   - Add a new variable named ENABLE_PIPELINE with value 'true'\n")

    panel = Panel(
        instructions, 
        title="GitHub Secret Setup Instructions", 
        expand=False,
        border_style="green"
    )
    console.print(panel)


def main(
    repo: str = typer.Option(..., help="GitHub repository in format owner/repo"),
    account_id: str = typer.Option(..., help="AWS Account ID"),
    region: str = typer.Option("us-east-1", help="AWS Region"),
    role_name: str = typer.Option("GitHubActionsCDKRole", help="Name for the IAM role"),
    ref: str = typer.Option("refs/heads/main", help="Git reference to authorize"),
) -> None:
    """Set up GitHub OIDC integration with AWS for CDK deployment."""
    
    # Create AWS clients
    try:
        iam_client = boto3.client("iam", region_name=region)
    except Exception as e:
        console.print(f"Error creating AWS client: {str(e)}")
        console.print("Make sure you have AWS credentials configured properly.")
        sys.exit(1)
        
    # Verify inputs
    if "/" not in repo:
        console.print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)
        
    # Get the thumbprint for GitHub's OIDC provider
    thumbprint = get_github_oidc_thumbprint()
    
    # Create or get the OIDC provider
    provider_arn = create_oidc_provider(iam_client, thumbprint)
    
    # Create the trust policy
    trust_policy = create_trust_policy(provider_arn, repo, ref)
    
    # Create or update the IAM role
    role_arn = create_iam_role(iam_client, role_name, trust_policy)
    
    # Create and attach the CDK policy
    cdk_policy = create_cdk_policy()
    attach_inline_policy(iam_client, role_name, cdk_policy)
    
    # Display success message and instructions
    console.print("\nu2705 GitHub OIDC integration setup complete!\n", style="bold green")
    console.print(f"OIDC Provider ARN: {provider_arn}")
    console.print(f"IAM Role ARN: {role_arn}")
    
    # Generate GitHub secret instructions
    generate_github_secret_instructions(role_arn)
    
    console.print("\nYou can now use GitHub Actions to deploy your CDK stacks securely!")


if __name__ == "__main__":
    typer.run(main)
