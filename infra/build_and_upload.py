#!/usr/bin/env python3

import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime
import boto3
import typer
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize typer app
app = typer.Typer(help="Build and upload artifacts to S3")

# Default values
DEFAULT_PROJECT_DIR = Path(__file__).parent.parent
DEFAULT_ENV = "dev"
DEFAULT_PROJECT_NAME = "python-libs"


def get_s3_client():
    """Get S3 client configured for LocalStack"""
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
    )


def create_bucket_if_not_exists(bucket_name):
    """Create S3 bucket if it doesn't exist"""
    s3_client = get_s3_client()
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        typer.echo(f"Bucket {bucket_name} already exists")
    except Exception:
        typer.echo(f"Creating bucket {bucket_name}")
        s3_client.create_bucket(Bucket=bucket_name)


def build_pyinstaller_executable(
    project_dir, temp_dir, entry_point="src/runners/run.py"
):
    """Build PyInstaller executable"""
    typer.echo("Building PyInstaller executable...")

    # Determine platform-specific settings
    is_windows = platform.system().lower() == "windows"
    exe_extension = ".exe" if is_windows else ""

    # Define output directory and executable name
    dist_dir = os.path.join(temp_dir, "dist")
    executable_name = f"pomodoro{exe_extension}"

    # Build the PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        "--name",
        "pomodoro",
        "--add-data",
        f"resources/sounds:resources/sounds",
        "--add-data",
        f".env:.env",
        os.path.join(project_dir, entry_point),
    ]

    # Add platform-specific options
    if is_windows:
        pyinstaller_cmd.extend(["--windowed"])  # No console window on Windows

    # Run PyInstaller
    subprocess.run(pyinstaller_cmd, cwd=project_dir, check=True)

    # Copy the executable to the temp directory
    src_executable = os.path.join(project_dir, "dist", executable_name)
    dst_executable = os.path.join(temp_dir, executable_name)
    shutil.copy2(src_executable, dst_executable)

    return dst_executable


def create_linux_script(project_dir, temp_dir):
    """Create a Linux shell script wrapper"""
    typer.echo("Creating Linux shell script...")

    script_content = """#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python script with the arguments
python "$SCRIPT_DIR/src/runners/run.py" "$@"
"""

    script_path = os.path.join(temp_dir, "run_pomodoro.sh")
    with open(script_path, "w") as f:
        f.write(script_content)

    # Make the script executable
    os.chmod(script_path, 0o755)

    return script_path


def upload_to_s3(file_path, bucket_name, s3_key):
    """Upload file to S3 bucket"""
    typer.echo(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
    s3_client = get_s3_client()
    with open(file_path, "rb") as f:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=f.read(),
        )


@app.command()
def build_and_upload(
    project_dir: Path = DEFAULT_PROJECT_DIR,
    env: str = DEFAULT_ENV,
    project_name: str = DEFAULT_PROJECT_NAME,
):
    """Build and upload artifacts to S3"""
    # Calculate bucket name
    bucket_name = f"{project_name}-artifacts-{env}"

    # Ensure bucket exists
    create_bucket_if_not_exists(bucket_name)

    # Create a temporary directory for artifacts
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate timestamp for versioning
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Build PyInstaller executable
        executable_path = build_pyinstaller_executable(project_dir, temp_dir)

        # Create Linux shell script
        script_path = create_linux_script(project_dir, temp_dir)

        # Determine platform-specific information
        platform_name = platform.system().lower()

        # Upload executable to S3
        executable_key = f"binaries/{platform_name}/pomodoro-{timestamp}{'.exe' if platform_name == 'windows' else ''}"
        upload_to_s3(executable_path, bucket_name, executable_key)

        # Upload shell script to S3 (for Linux only)
        if platform_name != "windows":
            script_key = f"binaries/linux/run_pomodoro-{timestamp}.sh"
            upload_to_s3(script_path, bucket_name, script_key)

        # Create a source archive
        source_archive = shutil.make_archive(
            os.path.join(temp_dir, f"{project_name}-{timestamp}"),
            "zip",
            project_dir,
        )

        # Upload source archive to S3
        source_key = f"source/{project_name}-{timestamp}.zip"
        upload_to_s3(source_archive, bucket_name, source_key)

        typer.echo("\nArtifacts successfully built and uploaded:")
        typer.echo(f"  - Executable: s3://{bucket_name}/{executable_key}")
        if platform_name != "windows":
            typer.echo(f"  - Shell script: s3://{bucket_name}/{script_key}")
        typer.echo(f"  - Source archive: s3://{bucket_name}/{source_key}")


if __name__ == "__main__":
    app()
