# Python-Libs

A cross-platform compatible collection of Python utilities and features including a Pomodoro timer, custom mocking framework, and infrastructure deployment.

## Project Overview

This project serves as a monorepo containing various Python utilities and features:

- **Pomodoro Timer**: A simple Pomodoro timer with sound notifications
- **Custom Mocking Framework**: A flexible framework for mocking in tests
- **Infrastructure as Code**: AWS CDK implementation for artifact deployment

## Key Features

- **Cross-Platform Compatibility**: Works on both Windows and Linux
- **Modular Design**: Components can be used independently
- **Comprehensive Testing**: Unit tests and behavior tests using pytest and behave
- **Infrastructure as Code**: AWS CDK for deployment infrastructure

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

## Infrastructure Deployment

### Setting Up LocalStack

1. Install infrastructure dependencies:

```bash
cd infra
make install
```

2. Start LocalStack:

```bash
make localstack-start
```

3. Deploy the infrastructure:

```bash
make deploy
```

### Building and Uploading Artifacts

```bash
make build-upload
```

This will:
- Build a PyInstaller executable (.exe on Windows, binary on Linux)
- Create a shell script wrapper for Linux
- Package the source code
- Upload all artifacts to the S3 bucket in LocalStack

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
