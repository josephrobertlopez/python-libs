#!/usr/bin/env python3

import os
import sys
import uuid
import boto3
import shutil
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
import typer
from typing import Optional
from dotenv import load_dotenv

app = typer.Typer(help="End-to-end deployment script using LocalStack")

# Load environment variables
load_dotenv()

# Constants
PROJECT_NAME = os.getenv("PROJECT_NAME", "python-libs")
REGION = os.getenv("AWS_REGION", "us-east-1")
ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")

def get_unique_bucket_name(base_name: str) -> str:
    """Generate a unique bucket name with a timestamp and random suffix"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = str(uuid.uuid4())[:6]
    return f"{base_name}-{timestamp}-{random_suffix}"

def check_localstack_running():
    """Check if LocalStack is running"""
    try:
        # Try to connect to the LocalStack health endpoint
        boto3.client(
            's3',
            endpoint_url=ENDPOINT_URL,
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name=REGION
        ).list_buckets()
        return True
    except Exception as e:
        typer.echo(f"LocalStack error: {e}")
        return False

def create_source_zip(project_dir: Path, temp_dir: Path) -> Path:
    """Create a zip archive of the source code"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_path = temp_dir / f"{PROJECT_NAME}-source-{timestamp}.zip"
    
    typer.echo(f"Creating source archive at {zip_path}...")
    
    # Create a temporary zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the project directory
        for root, dirs, files in os.walk(project_dir):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'dist', 'build']]
            
            # Add files to the zip
            for file in files:
                if file.endswith(('.pyc', '.pyo', '.pyd', '.so', '.DS_Store')):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)
                zipf.write(file_path, arcname)
    
    typer.echo(f"Source archive created: {zip_path}")
    return zip_path

@app.command()
def deploy(
    bucket_name: Optional[str] = None,
    region: str = REGION,
    project_dir: Path = Path.cwd().parent,
):
    """Deploy artifacts to S3 using LocalStack"""
    if not check_localstack_running():
        typer.echo("LocalStack is not running. Starting it now...")
        try:
            # Try to start LocalStack using our setup script
            os.system("python localstack_setup.py start")
            if not check_localstack_running():
                typer.echo("Failed to start LocalStack. Please start it manually.")
                sys.exit(1)
        except Exception as e:
            typer.echo(f"Error starting LocalStack: {e}")
            sys.exit(1)
    
    # Generate a unique bucket name if not provided
    if not bucket_name:
        bucket_name = f"{PROJECT_NAME}-artifacts-dev"
    
    typer.echo(f"Using LocalStack endpoint: {ENDPOINT_URL}")
    typer.echo(f"Project directory: {project_dir}")
    
    # Create S3 client with LocalStack endpoint
    s3_client = boto3.client(
        's3',
        endpoint_url=ENDPOINT_URL,
        region_name=region,
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )
    
    # Check if bucket exists, create if not
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        typer.echo(f"Bucket '{bucket_name}' already exists")
    except Exception:
        typer.echo(f"Creating bucket '{bucket_name}'...")
        s3_client.create_bucket(Bucket=bucket_name)
        
        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        typer.echo(f"Bucket '{bucket_name}' created successfully with versioning enabled")
    
    # Create a temporary directory for artifacts
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        
        # Create source code zip
        source_zip = create_source_zip(project_dir, temp_dir)
        
        # Upload source zip to S3
        source_key = f"source/{source_zip.name}"
        typer.echo(f"Uploading {source_zip} to s3://{bucket_name}/{source_key}...")
        
        with open(source_zip, 'rb') as file_data:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=source_key,
                Body=file_data
            )
        
        # Create a small test file with metadata
        readme_path = project_dir / "README.md"
        if readme_path.exists():
            readme_key = "docs/README.md"
            typer.echo(f"Uploading {readme_path} to s3://{bucket_name}/{readme_key}...")
            
            with open(readme_path, 'rb') as file_data:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=readme_key,
                    Body=file_data,
                    Metadata={
                        'DeployTime': datetime.now().isoformat(),
                        'Project': PROJECT_NAME
                    }
                )
    
    # List objects in the bucket
    typer.echo(f"\nListing objects in bucket '{bucket_name}'...")
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    for obj in response.get('Contents', []):
        typer.echo(f"- {obj['Key']} ({obj['Size']} bytes)")
    
    # Generate a pre-signed URL for each object (valid for 1 hour)
    typer.echo("\nPre-signed URLs for accessing the uploaded files (valid for 1 hour):")
    for obj in response.get('Contents', []):
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': obj['Key']},
            ExpiresIn=3600
        )
        typer.echo(f"- {obj['Key']}: {url}")
    
    typer.echo(f"\nDeployment complete! Objects have been uploaded to bucket: {bucket_name}")
    typer.echo("This bucket is in your LocalStack environment and will persist until you stop LocalStack.")

@app.command()
def cleanup(bucket_name: str):
    """Empty and delete an S3 bucket in LocalStack"""
    if not check_localstack_running():
        typer.echo("LocalStack is not running. Please start it first.")
        sys.exit(1)
    
    s3_client = boto3.client(
        's3',
        endpoint_url=ENDPOINT_URL,
        region_name=REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )
    
    # Confirm deletion
    confirm = typer.confirm(f"Are you sure you want to delete ALL objects in bucket '{bucket_name}' and the bucket itself?")
    if not confirm:
        typer.echo("Operation cancelled.")
        return
    
    try:
        # Delete all objects (no need to worry about versions in LocalStack)
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            for obj in response['Contents']:
                s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                typer.echo(f"Deleted object: {obj['Key']}")
        
        # Delete the bucket
        s3_client.delete_bucket(Bucket=bucket_name)
        typer.echo(f"Bucket '{bucket_name}' has been emptied and deleted.")
    except Exception as e:
        typer.echo(f"Error cleaning up bucket: {e}")
        sys.exit(1)

if __name__ == "__main__":
    app()
