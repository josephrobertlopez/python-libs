from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class ArtifactStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, project_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket for storing artifacts
        self.artifact_bucket = s3.Bucket(
            self,
            "ArtifactBucket",
            bucket_name=f"{project_name}-artifacts-{env_name}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,  # For development; use RETAIN in production
            auto_delete_objects=True,  # For development; set to False in production
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="expire-old-versions",
                    enabled=True,
                    noncurrent_version_expiration=s3.NoncurrentVersionExpiration(days=30),
                ),
            ],
        )

        # Create paths for different artifacts
        self.binary_path = "binaries/"
        self.source_path = "source/"

        # Output the bucket name and artifact paths
        CfnOutput(
            self,
            "ArtifactBucketName",
            value=self.artifact_bucket.bucket_name,
            description="Name of the S3 bucket for artifacts",
            export_name=f"{project_name}-artifact-bucket-name",
        )

        CfnOutput(
            self,
            "BinaryPath",
            value=self.binary_path,
            description="Path for binary artifacts in the S3 bucket",
            export_name=f"{project_name}-binary-path",
        )

        CfnOutput(
            self,
            "SourcePath",
            value=self.source_path,
            description="Path for source artifacts in the S3 bucket",
            export_name=f"{project_name}-source-path",
        )
