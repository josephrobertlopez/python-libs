from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
    Duration,
)
from constructs import Construct


class ArtifactStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        project_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket for storing artifacts
        self.artifact_bucket = s3.Bucket(
            self,
            "ArtifactBucket",
            bucket_name=f"{project_name}-artifacts-{env_name}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,  # For development; use RETAIN in production
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="expire-old-versions",
                    enabled=True,
                    noncurrent_version_expiration=Duration.days(30),
                ),
                # Add lifecycle rule for test logs expiration (7 days)
                s3.LifecycleRule(
                    id="expire-test-logs",
                    enabled=True,
                    expiration=Duration.days(7),
                    prefix="test-logs/",
                ),
                # Add lifecycle rule for CodePipeline artifacts (30 days)
                s3.LifecycleRule(
                    id="expire-pipeline-artifacts",
                    enabled=True,
                    expiration=Duration.days(30),
                    prefix="codepipeline/",
                ),
            ],
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                    max_age=3000,
                )
            ],
        )

        # Create paths for different artifacts
        self.binary_path = "binaries/"
        self.source_path = "source/"
        self.test_logs_path = "test-logs/"
        self.build_artifacts_path = "build-artifacts/"
        self.final_artifacts_path = "final-artifacts/"
        self.codepipeline_path = "codepipeline/"

        # Create IAM policy for CodePipeline to access the bucket
        codepipeline_policy = iam.PolicyStatement(
            actions=[
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:PutObject",
                "s3:ListBucket",
                "s3:DeleteObject",
            ],
            resources=[
                self.artifact_bucket.bucket_arn,
                f"{self.artifact_bucket.bucket_arn}/*",
            ],
        )

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

        CfnOutput(
            self,
            "TestLogsPath",
            value=self.test_logs_path,
            description="Path for test logs in the S3 bucket",
            export_name=f"{project_name}-test-logs-path",
        )

        CfnOutput(
            self,
            "BuildArtifactsPath",
            value=self.build_artifacts_path,
            description="Path for build artifacts in the S3 bucket",
            export_name=f"{project_name}-build-artifacts-path",
        )

        CfnOutput(
            self,
            "FinalArtifactsPath",
            value=self.final_artifacts_path,
            description="Path for final artifacts in the S3 bucket",
            export_name=f"{project_name}-final-artifacts-path",
        )

        CfnOutput(
            self,
            "CodePipelinePath",
            value=self.codepipeline_path,
            description="Path for CodePipeline artifacts in the S3 bucket",
            export_name=f"{project_name}-codepipeline-path",
        )
