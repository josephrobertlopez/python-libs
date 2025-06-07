#!/usr/bin/env python3

import os
import subprocess
import time
import typer
import boto3
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

app = typer.Typer(help="Setup and manage LocalStack for development")


def get_localstack_endpoint():
    return os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")


def get_aws_credentials():
    return {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", "test"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        "region_name": os.getenv("AWS_REGION", "us-east-1"),
    }


def check_localstack_running():
    """Check if LocalStack is running"""
    try:
        # Try to connect to the LocalStack health endpoint
        endpoint = get_localstack_endpoint()
        boto3.client(
            "s3",
            endpoint_url=endpoint,
            **get_aws_credentials(),
        ).list_buckets()
        return True
    except Exception:
        return False


@app.command()
def start():
    """Start LocalStack in detached mode"""
    if check_localstack_running():
        typer.echo("LocalStack is already running")
        return

    typer.echo("Starting LocalStack...")
    subprocess.run(
        ["docker", "run", "-d", "--name", "python-libs-localstack", "-p", "4566:4566", "-p", "4510-4559:4510-4559", "localstack/localstack:latest"],
        check=True,
    )

    # Wait for LocalStack to be ready
    max_retries = 10
    for i in range(max_retries):
        typer.echo(f"Waiting for LocalStack to be ready (attempt {i+1}/{max_retries})...")
        if check_localstack_running():
            typer.echo("LocalStack is now running")
            return
        time.sleep(5)

    typer.echo("Failed to start LocalStack after multiple attempts")
    raise typer.Exit(code=1)


@app.command()
def stop():
    """Stop and remove the LocalStack container"""
    typer.echo("Stopping LocalStack...")
    subprocess.run(["docker", "stop", "python-libs-localstack"], check=False)
    subprocess.run(["docker", "rm", "python-libs-localstack"], check=False)
    typer.echo("LocalStack stopped")


@app.command()
def status():
    """Check if LocalStack is running"""
    if check_localstack_running():
        typer.echo("LocalStack is running")
    else:
        typer.echo("LocalStack is not running")


@app.command()
def restart():
    """Restart LocalStack"""
    stop()
    start()


@app.command()
def list_buckets():
    """List S3 buckets in LocalStack"""
    if not check_localstack_running():
        typer.echo("LocalStack is not running. Start it first.")
        raise typer.Exit(code=1)

    s3_client = boto3.client(
        "s3",
        endpoint_url=get_localstack_endpoint(),
        **get_aws_credentials(),
    )
    response = s3_client.list_buckets()
    buckets = response.get("Buckets", [])

    if not buckets:
        typer.echo("No S3 buckets found")
        return

    typer.echo("S3 buckets:")
    for bucket in buckets:
        typer.echo(f"  - {bucket['Name']}")


@app.command()
def list_objects(bucket_name: str):
    """List objects in an S3 bucket"""
    if not check_localstack_running():
        typer.echo("LocalStack is not running. Start it first.")
        raise typer.Exit(code=1)

    s3_client = boto3.client(
        "s3",
        endpoint_url=get_localstack_endpoint(),
        **get_aws_credentials(),
    )
    
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        objects = response.get("Contents", [])

        if not objects:
            typer.echo(f"No objects found in bucket '{bucket_name}'")
            return

        typer.echo(f"Objects in bucket '{bucket_name}':")
        for obj in objects:
            typer.echo(f"  - {obj['Key']} ({obj['Size']} bytes)")
    except Exception as e:
        typer.echo(f"Error listing objects: {e}")
        raise typer.Exit(code=1)


@app.command()
def create_bucket(bucket_name: Optional[str] = None):
    """Create an S3 bucket for artifacts in LocalStack"""
    if not check_localstack_running():
        typer.echo("LocalStack is not running. Start it first.")
        raise typer.Exit(code=1)
    
    # Use the default naming convention if no name provided
    if not bucket_name:
        bucket_name = "python-libs-artifacts-dev"
    
    s3_client = boto3.client(
        "s3",
        endpoint_url=get_localstack_endpoint(),
        **get_aws_credentials(),
    )
    try:
        # Check if bucket already exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            typer.echo(f"Bucket '{bucket_name}' already exists")
            return bucket_name
        except Exception:
            # If a 404 error, the bucket does not exist
            pass  # Bucket doesn't exist, we'll create it
        
        # Create the bucket
        s3_client.create_bucket(Bucket=bucket_name)
        
        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        typer.echo(f"Created S3 bucket '{bucket_name}' with versioning enabled")
        return bucket_name
    
    except Exception as e:
        typer.echo(f"Error creating bucket: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
