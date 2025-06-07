#!/usr/bin/env python3

import os
import sys
import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

app = typer.Typer(help="Setup script for LocalStack CDK and CodePipeline integration")
console = Console()

def check_prerequisites():
    """Check if all required tools are installed"""
    prerequisites = [
        ("docker", "Docker is required to run LocalStack"),
        ("aws", "AWS CLI is required to interact with LocalStack"),
        ("npm", "npm is required to install cdklocal"),
        ("cdklocal", "cdklocal is required to deploy CDK stacks to LocalStack"),
        ("python", "Python 3.9+ is required to run the scripts"),
    ]
    
    missing = []
    for cmd, desc in prerequisites:
        if os.system(f"which {cmd} > /dev/null 2>&1") != 0:
            missing.append((cmd, desc))
    
    return missing

def create_env_file():
    """Create a default .env file if it doesn't exist"""
    env_path = Path(".env")
    
    if env_path.exists():
        return False
    
    with open(env_path, "w") as f:
        f.write("""
# Environment settings
ENVIRONMENT=dev
PROJECT_NAME=python-libs

# LocalStack settings
LOCALSTACK_ENDPOINT=http://localhost:4566

# AWS settings (for LocalStack)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1

# CDK settings
CDK_DEFAULT_ACCOUNT=000000000000
CDK_DEFAULT_REGION=us-east-1

# Pipeline settings
ENABLE_PIPELINE=false
""")
    
    return True

@app.command()
def install():
    """Install all dependencies and set up the environment"""
    # Check prerequisites
    missing = check_prerequisites()
    if missing:
        console.print(Panel.fit(
            "\n".join([f"[red]❌ {cmd}[/red]: {desc}" for cmd, desc in missing]),
            title="[bold red]Missing Prerequisites[/bold red]",
            border_style="red"
        ))
        console.print("\nPlease install the missing prerequisites and try again.")
        return
    
    # Create .env file
    if create_env_file():
        console.print("[green]✅ Created .env file with default settings[/green]")
    else:
        console.print("[yellow]⚠️ .env file already exists, skipping creation[/yellow]")
    
    # Install Python dependencies
    console.print("\n[bold]Installing Python dependencies...[/bold]")
    os.system("poetry install")
    
    # Install cdklocal if not already installed
    if os.system("which cdklocal > /dev/null 2>&1") != 0:
        console.print("\n[bold]Installing cdklocal...[/bold]")
        os.system("npm install -g aws-cdk-local")
    
    # Start LocalStack
    console.print("\n[bold]Starting LocalStack...[/bold]")
    os.system("python localstack_setup.py start")
    
    # Bootstrap CDK environment
    console.print("\n[bold]Bootstrapping CDK environment...[/bold]")
    os.system("make bootstrap")
    
    # Success message
    console.print(Panel.fit(
        "Your environment is now set up! Here are some commands you can try:\n\n"
        "[bold]make deploy[/bold] - Deploy the artifact bucket to LocalStack\n"
        "[bold]make deploy-with-pipeline[/bold] - Deploy with CodePipeline support\n"
        "[bold]python simulate_pipeline.py simulate-pipeline[/bold] - Simulate a CI/CD pipeline run\n"
        "[bold]python access_artifacts.py list-pipelines[/bold] - List pipeline runs\n"
        "[bold]make help[/bold] - See all available commands",
        title="[bold green]Setup Complete![/bold green]",
        border_style="green"
    ))

@app.command()
def status():
    """Check the status of the environment"""
    # Load environment variables
    load_dotenv()
    
    # Check LocalStack status
    console.print("[bold]Checking LocalStack status...[/bold]")
    ls_status = os.system("python localstack_setup.py status") == 0
    
    # Check environment variables
    env_vars = {
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "Not set"),
        "PROJECT_NAME": os.getenv("PROJECT_NAME", "Not set"),
        "LOCALSTACK_ENDPOINT": os.getenv("LOCALSTACK_ENDPOINT", "Not set"),
        "AWS_REGION": os.getenv("AWS_REGION", "Not set"),
        "ENABLE_PIPELINE": os.getenv("ENABLE_PIPELINE", "false"),
    }
    
    # Create a table for environment variables
    table = Table(title="Environment Variables")
    table.add_column("Variable", style="cyan")
    table.add_column("Value", style="green")
    
    for var, value in env_vars.items():
        table.add_row(var, value)
    
    console.print(table)
    
    # Check bucket status
    console.print("\n[bold]Checking S3 bucket status...[/bold]")
    bucket_cmd = "AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws --endpoint-url=http://localhost:4566 s3 ls"
    os.system(bucket_cmd)
    
    # Overall status
    if ls_status:
        console.print("\n[green]✅ Environment is ready to use![/green]")
    else:
        console.print("\n[yellow]⚠️ LocalStack is not running. Run 'python localstack_setup.py start' to start it.[/yellow]")

if __name__ == "__main__":
    app()
