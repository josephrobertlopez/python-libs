# Infrastructure as Code for Python-Libs

This directory contains the infrastructure as code (IaC) implementation for the Python-Libs project using AWS CDK with Python. It sets up an S3 bucket for storing artifacts and provides scripts for building and uploading binaries.

## Prerequisites

- Python 3.8 or higher
- Docker (for LocalStack)
- AWS CDK CLI (`npm install -g aws-cdk`)
- PyInstaller

## Setup

1. Install the required dependencies:

```bash
make install
```

2. Copy the example environment file and modify as needed:

```bash
cp .env.example .env
```

3. Start LocalStack (local AWS emulator):

```bash
make localstack-start
```

## Deploying Infrastructure

To deploy the infrastructure to LocalStack:

```bash
make deploy
```

This will create an S3 bucket in LocalStack for storing artifacts.

## Building and Uploading Artifacts

To build the application and upload artifacts to the S3 bucket:

```bash
make build-upload
```

This script will:
1. Create a PyInstaller executable (.exe on Windows, binary on Linux/Mac)
2. Create a shell script wrapper for Linux
3. Create a source code archive
4. Upload all artifacts to the S3 bucket

## Managing LocalStack

- Start LocalStack: `make localstack-start`
- Stop LocalStack: `make localstack-stop`
- Check status: `python localstack_setup.py status`
- List buckets: `python localstack_setup.py list-buckets`
- List objects in a bucket: `python localstack_setup.py list-objects BUCKET_NAME`

## Project Structure

```
infra/
├── cdk/                    # CDK application code
│   ├── app.py              # Main CDK application
│   └── stacks/             # CDK stack definitions
│       └── artifact_stack.py # S3 bucket stack
├── build_and_upload.py     # Script to build and upload artifacts
├── localstack_setup.py     # Script to manage LocalStack
├── Makefile                # Utility commands
├── requirements.txt        # Python dependencies
└── .env.example           # Example environment variables
```

## Environment Variables

The following environment variables can be set in the `.env` file:

- `AWS_ENDPOINT_URL`: LocalStack endpoint URL (default: http://localhost:4566)
- `AWS_REGION`: AWS region (default: us-east-1)
- `AWS_ACCESS_KEY_ID`: AWS access key ID for LocalStack (default: test)
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key for LocalStack (default: test)
- `ENVIRONMENT`: Deployment environment (default: dev)
- `PROJECT_NAME`: Project name (default: python-libs)

## Using the S3 Bucket with LocalStack

You can create and use the S3 bucket directly with the AWS CLI or boto3:

### Using AWS CLI

```bash
# List buckets
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws --endpoint-url=http://localhost:4566 s3 ls

# List bucket contents
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws --endpoint-url=http://localhost:4566 s3 ls s3://python-libs-artifacts-dev/

# Upload a file
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws --endpoint-url=http://localhost:4566 s3 cp example.txt s3://python-libs-artifacts-dev/example.txt
```

### Using boto3 (Python)

You can use the `create_s3_bucket.py` script to create the bucket and upload files:

```bash
python create_s3_bucket.py
```

Or in your own Python code:

```python
import boto3

# Create S3 client
s3_client = boto3.client(
    's3',
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

# Create bucket
s3_client.create_bucket(Bucket="python-libs-artifacts-dev")

# Upload file
with open("example.txt", 'rb') as file_data:
    s3_client.put_object(
        Bucket="python-libs-artifacts-dev", 
        Key="example.txt", 
        Body=file_data
    )
```

## CodePipeline Artifact Storage

The project now includes an enhanced artifact storage system designed to work with AWS CodePipeline. The CDK stack has been updated to support different types of pipeline artifacts including:

- Source code archives (`source/`)
- Test logs (`test-logs/`)
- Build artifacts (`build-artifacts/`)
- Final executables (`final-artifacts/`)
- Pipeline metadata (`codepipeline/`)

### Lifecycle Management

The S3 bucket has been configured with lifecycle rules for each artifact type:

- Test logs expire after 7 days
- CodePipeline artifacts expire after 30 days
- Non-current versions of any objects expire after 30 days

### Using the Simulation Tools

Two scripts are provided to demonstrate how CodePipeline would interact with the artifact bucket:

1. `simulate_pipeline.py` - Simulates a complete CI/CD pipeline run:

   ```bash
   # Run a complete pipeline simulation
   python simulate_pipeline.py simulate-pipeline
   
   # Generate a pre-signed URL for a specific artifact
   python simulate_pipeline.py get-presigned-url final-artifacts/pomodoro-1234567890
   ```

2. `access_artifacts.py` - Provides tools to access and manage artifacts:

   ```bash
   # List all pipeline runs
   python access_artifacts.py list-pipelines
   
   # Show details of a specific pipeline run
   python access_artifacts.py show-pipeline 1234567890
   
   # List all final artifacts (executables)
   python access_artifacts.py list-final-artifacts
   
   # List all test logs
   python access_artifacts.py list-test-logs
   
   # Download an artifact
   python access_artifacts.py download-artifact test-logs/test-results-1234567890.log --output-path local_file.log
   ```

### Integrating with Real CodePipeline

To use this setup with a real AWS CodePipeline:

1. Deploy the artifact stack to AWS (not LocalStack) by using the AWS CLI credentials instead of the LocalStack endpoint
2. Reference the bucket in your CodePipeline configuration as the artifact store
3. Configure the pipeline stages to save artifacts to the appropriate paths in the bucket

See the AWS documentation for more details on [how to configure CodePipeline with an S3 artifact store](https://docs.aws.amazon.com/codepipeline/latest/userguide/tutorials-s3deploy.html).

## GitHub Actions Integration

The project includes several GitHub Actions workflows to automate testing, building, and deploying the infrastructure:

- **Python Static Code Analysis** - Runs linting and unit tests
- **CDK Deployment** - Deploys infrastructure to AWS
- **Pipeline Artifacts** - Builds and uploads artifacts 
- **LocalStack CDK Test** - Tests infrastructure with LocalStack

For detailed information about these workflows, including a diagram of how they interact, see [GitHub Actions Integration](./docs/github-actions-integration.md).

### Setting Up GitHub Actions

We use GitHub's OpenID Connect (OIDC) for secure AWS authentication instead of long-lived access keys. To set this up:

1. Create an IAM OIDC provider for GitHub Actions in your AWS account
2. Create an IAM role with permissions for CDK deployment and S3 operations
3. Configure the role's trust policy to allow GitHub Actions to assume it
4. Add the following GitHub secret:
   - `AWS_ROLE_TO_ASSUME` - ARN of the IAM role created above

You can also set the following GitHub variable:

- `ENABLE_PIPELINE` - Set to "true" to deploy the CodePipeline stack

See the [detailed instructions](./docs/github-actions-integration.md#secure-aws-authentication-with-openid-connect-oidc) for creating the OIDC provider and IAM role.

## Cleaning Up

To clean up build artifacts:

```bash
make clean
```

To stop and remove the LocalStack container:

```bash
make localstack-stop
