from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct


class CodePipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        artifact_bucket: s3.IBucket,
        env_name: str,
        project_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a CodeCommit repository (or use existing)
        # In a real scenario, you might want to use GitHub or another source
        code_repo = codecommit.Repository(
            self,
            "CodeRepo",
            repository_name=f"{project_name}-repo-{env_name}",
            description=f"Source code repository for {project_name}",
        )

        # Define the pipeline
        pipeline = codepipeline.Pipeline(
            self,
            "Pipeline",
            pipeline_name=f"{project_name}-pipeline-{env_name}",
            artifact_bucket=artifact_bucket,
            restart_execution_on_update=True,
        )

        # Source stage
        source_output = codepipeline.Artifact("SourceCode")
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="Source",
            repository=code_repo,
            output=source_output,
            branch="main",  # or specify your branch
        )

        # Add source stage
        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action],
        )

        # Build project
        build_project = codebuild.PipelineProject(
            self,
            "BuildProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
                privileged=True,  # for Docker
            ),
            environment_variables={
                "ARTIFACT_BUCKET": codebuild.BuildEnvironmentVariable(
                    value=artifact_bucket.bucket_name
                ),
                "ENVIRONMENT": codebuild.BuildEnvironmentVariable(value=env_name),
                "PROJECT_NAME": codebuild.BuildEnvironmentVariable(value=project_name),
            },
            build_spec=codebuild.BuildSpec.from_object(
                {
                    "version": "0.2",
                    "phases": {
                        "install": {
                            "runtime-versions": {
                                "python": "3.9",
                            },
                            "commands": [
                                "curl -sSL https://install.python-poetry.org | python3 -",
                                'export PATH="$HOME/.local/bin:$PATH"',
                                "poetry install",
                            ],
                        },
                        "build": {
                            "commands": [
                                # Run tests and generate coverage report
                                "poetry run pytest --cov=. --cov-report=xml:test-results/coverage.xml --junitxml=test-results/junit.xml",
                                # Build executables
                                "poetry run python -m PyInstaller --onefile app.py -n pomodoro",
                            ],
                        },
                        "post_build": {
                            "commands": [
                                # Upload test logs
                                "aws s3 cp test-results/ s3://${ARTIFACT_BUCKET}/test-logs/ --recursive",
                                # Upload build artifacts
                                "aws s3 cp dist/ s3://${ARTIFACT_BUCKET}/final-artifacts/ --recursive",
                                # Create metadata file
                                'echo "Build completed on `date`" > build-info.txt',
                                "aws s3 cp build-info.txt s3://${ARTIFACT_BUCKET}/codepipeline/build-info-${CODEBUILD_BUILD_ID}.txt",
                            ],
                        },
                    },
                    "artifacts": {
                        "files": [
                            "dist/**/*",
                            "test-results/**/*",
                        ],
                    },
                    "cache": {
                        "paths": [
                            "/root/.cache/pip",
                        ],
                    },
                }
            ),
        )

        # Grant permissions to the build project
        artifact_bucket.grant_read_write(build_project)

        # Build stage outputs
        build_output = codepipeline.Artifact("BuildOutput")

        # Build action
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output,
            outputs=[build_output],
        )

        # Add build stage
        pipeline.add_stage(
            stage_name="Build",
            actions=[build_action],
        )

        # Outputs
        CfnOutput(
            self,
            "PipelineName",
            value=pipeline.pipeline_name,
            description="Name of the CodePipeline",
        )

        CfnOutput(
            self,
            "CodeCommitRepoName",
            value=code_repo.repository_name,
            description="Name of the CodeCommit repository",
        )

        CfnOutput(
            self,
            "CodeCommitCloneUrlHttp",
            value=code_repo.repository_clone_url_http,
            description="HTTPS URL for cloning the CodeCommit repository",
        )
