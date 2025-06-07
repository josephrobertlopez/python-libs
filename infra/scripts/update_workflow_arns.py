#!/usr/bin/env python3

"""
Update GitHub Actions Workflow Role ARNs

This script updates the hardcoded IAM role ARN in all GitHub Actions workflow files
with the actual ARN you want to use. This is useful after setting up the OIDC role
with the setup_github_oidc.py script.

Usage:
    python update_workflow_arns.py [OPTIONS]

Options:
    --role-arn TEXT         The actual IAM role ARN to use  [required]
    --workflow-dir TEXT     Directory containing workflow files (default: .github/workflows)
    --help                  Show this message and exit.
"""

import glob
import os
import re
import sys

import typer
from rich.console import Console


console = Console()


def update_workflow_files(role_arn: str, workflow_dir: str) -> None:
    """Update IAM role ARN in GitHub Actions workflow files."""
    # Default placeholder ARN
    placeholder_arn = "arn:aws:iam::123456789012:role/GitHubActionsCDKRole"
    
    # Find all YAML files in the workflow directory
    workflow_files = glob.glob(os.path.join(workflow_dir, "*.yml"))
    
    if not workflow_files:
        console.print(f"No workflow files found in {workflow_dir}", style="yellow")
        return
    
    console.print(f"Found {len(workflow_files)} workflow files")
    
    for file_path in workflow_files:
        console.print(f"Processing {os.path.basename(file_path)}...")
        
        # Read the file content
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check if the file contains the placeholder ARN
        if placeholder_arn not in content:
            console.print(f"  No placeholder ARN found in {os.path.basename(file_path)}", style="yellow")
            continue
        
        # Replace the placeholder ARN with the actual ARN
        updated_content = content.replace(placeholder_arn, role_arn)
        
        # Write the updated content back to the file
        with open(file_path, "w") as f:
            f.write(updated_content)
        
        console.print(f"  Updated {os.path.basename(file_path)} with role ARN: {role_arn}", style="green")


def main(
    role_arn: str = typer.Option(..., help="The actual IAM role ARN to use"),
    workflow_dir: str = typer.Option(
        ".github/workflows", help="Directory containing workflow files"
    ),
) -> None:
    """Update GitHub Actions workflow files with your actual IAM role ARN."""
    
    # Validate the role ARN format
    if not role_arn.startswith("arn:aws:iam::") or ":role/" not in role_arn:
        console.print("Error: Invalid IAM role ARN format", style="bold red")
        console.print("ARN should look like: arn:aws:iam::123456789012:role/RoleName")
        sys.exit(1)
    
    # Check if the workflow directory exists
    if not os.path.isdir(workflow_dir):
        console.print(f"Error: Workflow directory '{workflow_dir}' not found", style="bold red")
        sys.exit(1)
    
    # Update the workflow files
    update_workflow_files(role_arn, workflow_dir)
    
    console.print("\nu2705 GitHub Actions workflow files updated successfully!", style="bold green")


if __name__ == "__main__":
    typer.run(main)
