#!/usr/bin/env python3

import os
import json
import boto3
import typer
from tabulate import tabulate
from datetime import datetime

app = typer.Typer(help="Access and manage artifacts in the S3 bucket")

# Constants
BUCKET_NAME = "python-libs-artifacts-dev"
ENDPOINT_URL = "http://localhost:4566"


# S3 client
def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@app.command()
def list_pipelines():
    """List all pipeline runs and their artifacts"""
    s3 = get_s3_client()

    # Get all pipeline metadata files
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="codepipeline/")

    if not response.get("Contents"):
        typer.echo("No pipeline runs found.")
        return

    pipeline_data = []

    for obj in response.get("Contents", []):
        if obj["Key"].endswith(".json"):
            # Get the pipeline metadata
            try:
                response = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                metadata = json.loads(response["Body"].read().decode("utf-8"))

                # Add to our list
                pipeline_data.append(
                    [
                        metadata.get("pipeline_id", "Unknown"),
                        metadata.get("timestamp", "Unknown"),
                        metadata.get("status", "Unknown"),
                        obj["Key"],
                    ]
                )
            except Exception as e:
                typer.echo(f"Error reading pipeline metadata {obj['Key']}: {e}")

    # Display as a table
    if pipeline_data:
        typer.echo("\nPipeline Runs:\n")
        print(
            tabulate(
                pipeline_data,
                headers=["Pipeline ID", "Timestamp", "Status", "Metadata File"],
                tablefmt="grid",
            )
        )
    else:
        typer.echo("No valid pipeline metadata found.")


@app.command()
def show_pipeline(pipeline_id: str):
    """Show details of a specific pipeline run"""
    s3 = get_s3_client()

    # Find the pipeline metadata
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="codepipeline/")

    metadata_key = None
    for obj in response.get("Contents", []):
        if pipeline_id in obj["Key"] and obj["Key"].endswith(".json"):
            metadata_key = obj["Key"]
            break

    if not metadata_key:
        typer.echo(f"Pipeline {pipeline_id} not found.")
        return

    # Get the pipeline metadata
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=metadata_key)
        metadata = json.loads(response["Body"].read().decode("utf-8"))

        typer.echo(f"\nPipeline: {metadata.get('pipeline_id')}")
        typer.echo(f"Timestamp: {metadata.get('timestamp')}")
        typer.echo(f"Status: {metadata.get('status')}")

        # List artifacts
        typer.echo("\nArtifacts:")
        artifacts = metadata.get("artifacts", {})
        for artifact_type, artifact_key in artifacts.items():
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET_NAME, "Key": artifact_key},
                ExpiresIn=3600,
            )
            typer.echo(f"  - {artifact_type}: {artifact_key}")
            typer.echo(f"    URL: {url}")

            # Get artifact metadata
            try:
                obj_metadata = s3.head_object(Bucket=BUCKET_NAME, Key=artifact_key)
                if "Metadata" in obj_metadata and obj_metadata["Metadata"]:
                    typer.echo(
                        f"    Metadata: {json.dumps(obj_metadata['Metadata'], indent=2)}"
                    )
            except Exception:
                pass

    except Exception as e:
        typer.echo(f"Error reading pipeline metadata: {e}")


@app.command()
def download_artifact(artifact_key: str, output_path: str = None):
    """Download an artifact from the S3 bucket"""
    s3 = get_s3_client()

    if output_path is None:
        output_path = os.path.basename(artifact_key)

    try:
        typer.echo(f"Downloading {artifact_key} to {output_path}...")
        s3.download_file(BUCKET_NAME, artifact_key, output_path)
        typer.echo(f"Successfully downloaded {artifact_key} to {output_path}")
    except Exception as e:
        typer.echo(f"Error downloading artifact: {e}")


@app.command()
def list_test_logs():
    """List all test logs"""
    s3 = get_s3_client()

    # Get all test logs
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="test-logs/")

    if not response.get("Contents"):
        typer.echo("No test logs found.")
        return

    typer.echo("\nTest Logs:\n")
    for obj in response.get("Contents", []):
        # Get object metadata
        try:
            obj_metadata = s3.head_object(Bucket=BUCKET_NAME, Key=obj["Key"])
            timestamp = obj_metadata.get("Metadata", {}).get("timestamp", "Unknown")
            typer.echo(f"- {obj['Key']} (Created: {timestamp})")
        except Exception:
            typer.echo(f"- {obj['Key']}")


@app.command()
def list_final_artifacts():
    """List all final artifacts (executables)"""
    s3 = get_s3_client()

    # Get all final artifacts
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="final-artifacts/")

    if not response.get("Contents"):
        typer.echo("No final artifacts found.")
        return

    artifacts = []
    for obj in response.get("Contents", []):
        # Get object metadata
        try:
            obj_metadata = s3.head_object(Bucket=BUCKET_NAME, Key=obj["Key"])
            timestamp = obj_metadata.get("Metadata", {}).get("timestamp", "Unknown")
            stage = obj_metadata.get("Metadata", {}).get("pipeline-stage", "Unknown")

            # Generate pre-signed URL
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET_NAME, "Key": obj["Key"]},
                ExpiresIn=3600,
            )

            artifacts.append([obj["Key"], timestamp, stage, obj["Size"], url])
        except Exception as e:
            artifacts.append([obj["Key"], "Error", "Error", obj["Size"], str(e)])

    # Display as a table
    if artifacts:
        typer.echo("\nFinal Artifacts:\n")
        print(
            tabulate(
                artifacts,
                headers=["Key", "Timestamp", "Stage", "Size", "Download URL"],
                tablefmt="grid",
            )
        )
    else:
        typer.echo("No final artifacts found.")


if __name__ == "__main__":
    app()
