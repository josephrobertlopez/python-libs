# Python-Libs

[![Python Static Code Analysis](https://github.com/josephrobertlopez/python-libs/actions/workflows/code-analysis.yml/badge.svg)](https://github.com/josephrobertlopez/python-libs/actions/workflows/code-analysis.yml)
[![CDK Deployment](https://github.com/josephrobertlopez/python-libs/actions/workflows/cdk-deployment.yml/badge.svg)](https://github.com/josephrobertlopez/python-libs/actions/workflows/cdk-deployment.yml)
[![Pipeline Artifacts](https://github.com/josephrobertlopez/python-libs/actions/workflows/pipeline-artifacts.yml/badge.svg)](https://github.com/josephrobertlopez/python-libs/actions/workflows/pipeline-artifacts.yml)
[![LocalStack CDK Test](https://github.com/josephrobertlopez/python-libs/actions/workflows/localstack-test.yml/badge.svg)](https://github.com/josephrobertlopez/python-libs/actions/workflows/localstack-test.yml)

A cross-platform compatible collection of Python utilities and features including a Pomodoro timer, custom mocking framework, and infrastructure deployment.

## Project Overview

This project serves as a monorepo containing various Python utilities and features:

- **Pomodoro Timer**: A simple Pomodoro timer with sound notifications
- **Smart Mocking Framework**: A flexible, resilient framework for mocking in tests with automatic type detection
- **Infrastructure as Code**: AWS CDK implementation for artifact deployment

## Key Features

- **Cross-Platform Compatibility**: Works on both Windows and Linux
- **Modular Design**: Components can be used independently
- **Comprehensive Testing**: Unit tests and behavior tests using pytest and behave
- **Smart Mocking**: Intelligent mocking system that handles any type of input
- **Infrastructure as Code**: AWS CDK for deployment infrastructure

## GitHub Actions Workflows

This project uses GitHub Actions for CI/CD with the following workflows:

See [Infrastructure README](./infra/README.md) for details on workflow setup and configuration.

### Setting Up GitHub OIDC for AWS Authentication

We use GitHub's OIDC integration for secure AWS authentication. Helper scripts are provided:

```bash
# Install requirements
pip install -r infra/scripts/requirements-oidc.txt

# 1. Create the IAM OIDC provider and role
python infra/scripts/setup_github_oidc.py --repo josephrobertlopez/python-libs --account-id 123456789012

# 2. Update workflow files with the correct role ARN
python infra/scripts/update_workflow_arns.py --role-arn "arn:aws:iam::123456789012:role/GitHubActionsCDKRole"
```

These scripts will:
1. Create an IAM OIDC provider for GitHub Actions
2. Create an IAM role with proper CDK deployment permissions
3. Update all workflow files with the correct role ARN

See [detailed instructions](./infra/docs/github-actions-integration.md#important-note-on-role-arn) for more information.

## Setup

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker (for LocalStack)
- AWS CDK CLI (`npm install -g aws-cdk`)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/python-libs.git
cd python-libs
```

2. Install dependencies:

```bash
poetry install
```

3. Create a `.env` file based on the example:

```bash
cp .env.example .env
```

## Testing

### Running Unit Tests

```bash
python -m pytest
```

### Running Behavior Tests

```bash
behave
```

## Using the Pomodoro Timer

```bash
python src/runners/run.py pomodoro -m 25
```

This sets a Pomodoro timer for 25 minutes.

## Using the Smart Mocking Framework

The smart mocking framework provides a resilient, type-aware mocking system that automatically detects the appropriate mocking strategy based on the input type.

```python
from src.utils.test.smart_mock import smart_mock, patch_object, create_mock_class

# Simple mocking with automatic type detection
with smart_mock(
    "my_module",
    function=lambda x: x * 2,
    config={"key": "value"},
    items=[1, 2, 3]
) as mock_ctx:
    # Use the mocks
    result = my_module.function(5)  # Returns 10
    
# Patch an object attribute or method
with patch_object(some_object, "method_name", lambda x: x + 1):
    result = some_object.method_name(5)  # Returns 6
    
# Create a mock class with methods and attributes
MockDB = create_mock_class(
    class_methods={"query": lambda: [{"id": 1}]},
    class_attributes={"connection_string": "mock://db"}
)
```

See [Smart Mocking Framework README](./src/utils/test/README.md) for more details and advanced usage.

## Infrastructure Deployment

### Setting Up LocalStack

1. Install infrastructure dependencies:

```bash
cd infra
make install
```

Alternatively, you can use our setup script for a guided experience:

```bash
cd infra
python setup.py install
```

2. Start LocalStack:

```bash
make localstack-start
```

3. Deploy the infrastructure:

```bash
make deploy           # Deploy just the artifact bucket
# OR
make deploy-with-pipeline  # Deploy with CodePipeline support
```

### Building and Uploading Artifacts

```bash
make build-upload     # Build and upload artifacts manually
# OR
make simulate-pipeline  # Simulate a complete CI/CD pipeline run
```

### Viewing and Managing Artifacts

```bash
make list-artifacts   # List all artifacts in the bucket

# For more detailed operations
python infra/access_artifacts.py list-pipelines
python infra/access_artifacts.py show-pipeline <pipeline-id>
python infra/access_artifacts.py list-final-artifacts
python infra/access_artifacts.py download-artifact <artifact-key> --output-path <local-path>
```

## Cross-Platform Compatibility

This codebase has been updated to ensure compatibility across different operating systems:

- Uses `os.path.join()` for platform-independent path construction
- Normalizes path separators in environment variables
- Provides detailed error messages with absolute paths
- Handles mocking of file system operations consistently

## Project Structure

```
python-libs/
├── features/            # Behave feature tests
├── infra/               # Infrastructure as Code
│   ├── cdk/             # AWS CDK implementation
│   ├── build_and_upload.py  # Artifact build and upload script
│   └── localstack_setup.py  # LocalStack management
├── resources/           # Application resources
│   ├── logs/            # Log files
│   └── sounds/          # Sound files
├── src/                 # Source code
│   ├── runners/         # CLI runners
│   └── utils/           # Utility modules
└── tests/               # Unit tests
```

For more details on individual components, see their respective README files:
- For local script executions view `src/runners/README.md`
- For infrastructure details view `infra/README.md`
