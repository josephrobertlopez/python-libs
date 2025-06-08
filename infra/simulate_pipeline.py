#!/usr/bin/env python3

import os
import json
import boto3
import typer
import tempfile
import time
from pathlib import Path
from datetime import datetime

app = typer.Typer(help="Simulate a CI/CD pipeline using the artifact bucket")

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
def simulate_pipeline():
    """Simulate a complete CI/CD pipeline process with artifact storage"""
    typer.echo(
        f"\n=== Starting Pipeline Simulation @ {datetime.now().isoformat()} ===\n"
    )

    # Phase 1: Source (checkout code)
    typer.echo("\n📦 PHASE 1: SOURCE CHECKOUT")
    source_artifact_key = f"source/source-{int(time.time())}.zip"
    with tempfile.NamedTemporaryFile(suffix=".zip") as source_zip:
        # Create a mock source zip
        with open(source_zip.name, "wb") as f:
            f.write(b"Mock source code content")

        # Upload source artifact
        typer.echo(f"Uploading source code to s3://{BUCKET_NAME}/{source_artifact_key}")
        get_s3_client().upload_file(
            source_zip.name,
            BUCKET_NAME,
            source_artifact_key,
            ExtraArgs={
                "Metadata": {
                    "pipeline-stage": "source",
                    "timestamp": datetime.now().isoformat(),
                }
            },
        )

    # Phase 2: Build (compile code, run unit tests)
    typer.echo("\n🔨 PHASE 2: BUILD AND TEST")

    # Create test logs
    test_logs_key = f"test-logs/test-results-{int(time.time())}.log"
    with tempfile.NamedTemporaryFile(suffix=".log") as test_log:
        # Create mock test logs
        test_content = f"""=== Test Results ===
Ran 42 tests in 2.5s

OK

Coverage: 87%
Test run: {datetime.now().isoformat()}
"""
        with open(test_log.name, "w") as f:
            f.write(test_content)

        # Upload test logs
        typer.echo(f"Uploading test logs to s3://{BUCKET_NAME}/{test_logs_key}")
        get_s3_client().upload_file(
            test_log.name,
            BUCKET_NAME,
            test_logs_key,
            ExtraArgs={
                "Metadata": {
                    "pipeline-stage": "test",
                    "timestamp": datetime.now().isoformat(),
                }
            },
        )

    # Create build artifacts
    build_artifact_key = f"build-artifacts/build-output-{int(time.time())}.zip"
    with tempfile.NamedTemporaryFile(suffix=".zip") as build_zip:
        # Create mock build artifact
        with open(build_zip.name, "wb") as f:
            f.write(b"Mock build artifact content")

        # Upload build artifact
        typer.echo(
            f"Uploading build artifacts to s3://{BUCKET_NAME}/{build_artifact_key}"
        )
        get_s3_client().upload_file(
            build_zip.name,
            BUCKET_NAME,
            build_artifact_key,
            ExtraArgs={
                "Metadata": {
                    "pipeline-stage": "build",
                    "timestamp": datetime.now().isoformat(),
                }
            },
        )

    # Phase 3: Package (create deployable artifacts)
    typer.echo("\n📦 PHASE 3: PACKAGE")

    # Create final executable artifact
    final_artifact_key = f"final-artifacts/pomodoro-{int(time.time())}"
    with tempfile.NamedTemporaryFile() as exe_file:
        # Create mock executable
        with open(exe_file.name, "wb") as f:
            f.write(b'#!/bin/bash\necho "This is a mock executable"\n')

        # Upload final artifact
        typer.echo(
            f"Uploading final executable to s3://{BUCKET_NAME}/{final_artifact_key}"
        )
        get_s3_client().upload_file(
            exe_file.name,
            BUCKET_NAME,
            final_artifact_key,
            ExtraArgs={
                "Metadata": {
                    "pipeline-stage": "package",
                    "timestamp": datetime.now().isoformat(),
                },
                "ContentType": "application/octet-stream",
                "ContentDisposition": "attachment",
            },
        )

    # Phase 4: Store pipeline metadata
    typer.echo("\n📝 PHASE 4: RECORDING PIPELINE METADATA")

    # Create pipeline metadata JSON
    pipeline_metadata = {
        "pipeline_id": f"pipeline-{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "artifacts": {
            "source": source_artifact_key,
            "test_logs": test_logs_key,
            "build": build_artifact_key,
            "final": final_artifact_key,
        },
        "status": "SUCCESS",
    }

    # Upload pipeline metadata
    pipeline_metadata_key = f"codepipeline/pipeline-run-{int(time.time())}.json"
    with tempfile.NamedTemporaryFile(suffix=".json") as metadata_file:
        # Write metadata JSON
        with open(metadata_file.name, "w") as f:
            json.dump(pipeline_metadata, f, indent=2)

        # Upload metadata
        typer.echo(
            f"Uploading pipeline metadata to s3://{BUCKET_NAME}/{pipeline_metadata_key}"
        )
        get_s3_client().upload_file(
            metadata_file.name,
            BUCKET_NAME,
            pipeline_metadata_key,
            ExtraArgs={"ContentType": "application/json"},
        )

    # List all artifacts
    typer.echo("\n🔍 LISTING ALL PIPELINE ARTIFACTS:")
    response = get_s3_client().list_objects_v2(Bucket=BUCKET_NAME)

    for obj in response.get("Contents", []):
        # Get metadata for the object
        try:
            obj_metadata = get_s3_client().head_object(
                Bucket=BUCKET_NAME, Key=obj["Key"]
            )
            metadata_str = json.dumps(obj_metadata.get("Metadata", {}), indent=2)
        except Exception:
            metadata_str = "{}"

        typer.echo(f"- {obj['Key']} ({obj['Size']} bytes)")
        if metadata_str != "{}":
            typer.echo(f"  Metadata: {metadata_str}")

    typer.echo(
        f"\n✅ Pipeline simulation completed successfully at {datetime.now().isoformat()}"
    )
    typer.echo("The bucket now contains all artifacts from the simulated pipeline run.")


@app.command()
def get_presigned_url(key: str):
    """Generate a pre-signed URL for accessing an artifact"""
    url = get_s3_client().generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET_NAME, "Key": key}, ExpiresIn=3600
    )
    typer.echo(f"Pre-signed URL for {key} (valid for 1 hour):\n{url}")


if __name__ == "__main__":
    app()
