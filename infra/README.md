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

## Cleaning Up

To clean up build artifacts:

```bash
make clean
```

To stop and remove the LocalStack container:

```bash
make localstack-stop
```
