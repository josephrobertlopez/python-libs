# GitHub Actions Integration with CDK Infrastructure

## Overview

This document explains how the GitHub Actions workflows integrate with our CDK infrastructure to provide continuous integration, testing, and deployment capabilities. The workflows are designed to work with both LocalStack for testing and real AWS for production deployments.

## Workflow Architecture

We have implemented the following GitHub Actions workflows:

1. **Python Static Code Analysis** - For code quality and testing
2. **CDK Deployment** - For deploying infrastructure to AWS
3. **Pipeline Artifacts** - For building and managing artifacts
4. **LocalStack CDK Test** - For testing infrastructure with LocalStack

### Workflow Diagram

```
+------------------------+     +------------------------+     +------------------------+
|                        |     |                        |     |                        |
| Code Analysis Workflow |     | LocalStack CDK Test    |     | Pipeline Artifacts     |
|                        |     | Workflow               |     | Workflow               |
+------------------------+     +------------------------+     +------------------------+
          |                              |                              |
          | On PR/Push                   | On PR with                   | On Push to main
          |                              | infra changes                | or schedule
          v                              v                              v
+------------------------+     +------------------------+     +------------------------+
|                        |     |                        |     |                        |
| Lint & Test Python     |     | Deploy & Validate      |     | Build & Upload         |
| Code                   |     | Infra on LocalStack    |     | Artifacts              |
|                        |     |                        |     |                        |
+------------------------+     +------------------------+     +------------------------+
                                                                          |
                                                                          |
                                                                          v
                                                              +------------------------+
                                                              |                        |
                                                              | Store in S3 Bucket     |
                                                              | (if on main branch)    |
                                                              |                        |
                                                              +------------------------+
                                                                          ^
                                                                          |
+------------------------+                                                |
|                        |                                                |
| CDK Deployment         |                                                |
| Workflow               |-----------------------------------------------+
|                        |
+------------------------+
          |
          | On Push to main
          | with infra changes
          v
+------------------------+     +------------------------+
|                        |     |                        |
| Validate with          |---->| Deploy to AWS          |
| LocalStack             |     | (if on main branch)    |
|                        |     |                        |
+------------------------+     +------------------------+
```

## Workflow Details

### 1. Python Static Code Analysis

This workflow runs on every push and pull request to the main branch. It performs:
- Linting with flake8
- Unit testing with pytest
- Code coverage reporting

### 2. CDK Deployment

This workflow is triggered by:
- Pushes to main branch affecting infrastructure files
- Manual triggering via workflow_dispatch

It consists of two jobs:

**Validation Job**:
- Tests CDK code with LocalStack
- Deploys stacks to LocalStack
- Simulates pipeline operation
- Verifies artifact accessibility

**Deployment Job** (only on main branch):
- Configures AWS credentials
- Bootstraps CDK in the target AWS account
- Deploys the artifact stack
- Conditionally deploys the pipeline stack if enabled

### 3. Pipeline Artifacts

This workflow is triggered by:
- Pushes to main branch affecting source code or tests
- Weekly scheduled runs
- Manual triggering

It performs:
- Running tests with coverage
- Building executable artifacts
- Packaging source code
- Uploading all artifacts to GitHub Actions artifacts storage
- Optionally uploading to S3 if running on main branch

### 4. LocalStack CDK Test

This workflow is specifically designed for testing infrastructure changes during pull requests. It:
- Sets up LocalStack in the GitHub Actions environment
- Validates CDK synthesis
- Deploys all stacks to LocalStack
- Runs pipeline simulation
- Verifies artifact storage and retrieval

## Setting Up GitHub Secrets

### Secure AWS Authentication with OpenID Connect (OIDC)

We've implemented GitHub's OpenID Connect (OIDC) integration for secure, short-lived AWS credentials instead of using long-lived AWS access keys. This approach is more secure because:

1. No long-lived credentials are stored in GitHub Secrets
2. AWS temporary credentials are automatically rotated
3. You can restrict permissions using IAM roles

#### How to Set Up OIDC with AWS:

1. Create an IAM OIDC Identity Provider in AWS:

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list $(curl -s https://token.actions.githubusercontent.com/.well-known/openid-configuration | jq -r '.jwks_uri' | xargs curl -s | jq -r '.keys[0].x5c[0]' | base64 -d | openssl x509 -fingerprint -noout | sed 's/.*=//' | tr -d ':' | tr '[:upper:]' '[:lower:]')
```

2. Create an IAM Role with the following trust policy (replace values with your repository):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:josephrobertlopez/python-libs:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

3. Attach the necessary IAM policies to this role for S3, CodePipeline, and CDK deployment permissions.

4. Store the role ARN as a GitHub Secret:
   - Create a new repository secret named `AWS_ROLE_TO_ASSUME` with the ARN of the IAM role

#### Permission Requirements

The IAM role needs these permissions:

- S3 bucket creation and management
- CloudFormation stack deployment
- CDK bootstrap and deployment
- CodePipeline, CodeBuild, and CodeCommit resource creation (if using the pipeline)

## Important Note on Role ARN

In the GitHub Actions workflow files, you'll notice a hardcoded role ARN placeholder:

```yaml
role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsCDKRole
```

This is used to avoid GitHub Actions lint warnings. **You must replace this with your actual IAM role ARN** before using these workflows. You can do this in one of two ways:

1. Directly edit the workflow files to replace the placeholder ARN with your actual ARN
2. Use the provided helper scripts:

```bash
# First, install requirements for the scripts
pip install -r infra/scripts/requirements-oidc.txt

# Run the setup script to create the OIDC provider and IAM role
python infra/scripts/setup_github_oidc.py --repo your-org/your-repo --account-id 123456789012

# Then update the workflow files with the generated role ARN
python infra/scripts/update_workflow_arns.py --role-arn "arn:aws:iam::123456789012:role/GitHubActionsCDKRole"
```

The role ARN from the setup script will look something like: `arn:aws:iam::123456789012:role/GitHubActionsCDKRole`

## GitHub Variables

The following repository variables can be set to control workflow behavior:

- `ENABLE_PIPELINE` - Set to "true" to deploy the CodePipeline stack

## Local Testing vs. AWS Deployment

Our workflows use different approaches for testing and production:

- **Testing**: Uses LocalStack with dummy AWS credentials
- **Production**: Uses real AWS credentials from GitHub Secrets

## Required Environments

The `CDK Deployment` workflow uses GitHub Environments for deployment protection:

- A "production" environment with appropriate protection rules should be configured
- This enables approval workflows and environment-specific secrets

## Cross-Platform Compatibility

While the GitHub Actions workflows run on Ubuntu runners, the infrastructure and scripts are designed to be cross-platform compatible for local development on Windows, macOS, and Linux.
