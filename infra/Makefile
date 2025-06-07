# Makefile for infrastructure management

.PHONY: install deploy synth bootstrap localstack-start localstack-stop build-upload clean help deploy-with-pipeline simulate-pipeline list-artifacts

help:
	@echo "Available commands:"
	@echo "  install             Install dependencies"
	@echo "  bootstrap           Bootstrap LocalStack environment for CDK"
	@echo "  deploy              Deploy infrastructure to LocalStack"
	@echo "  deploy-with-pipeline Deploy infrastructure with pipeline to LocalStack"
	@echo "  synth               Synthesize CloudFormation template"
	@echo "  localstack-start    Start LocalStack container"
	@echo "  localstack-stop     Stop LocalStack container"
	@echo "  build-upload        Build and upload artifacts"
	@echo "  simulate-pipeline   Simulate a CI/CD pipeline run"
	@echo "  list-artifacts      List artifacts in the bucket"
	@echo "  clean               Clean build artifacts"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

bootstrap:
	@echo "Bootstrapping LocalStack environment for CDK..."
	cd cdk && cdklocal bootstrap

synth:
	@echo "Synthesizing CloudFormation template..."
	cd cdk && python -m app

deploy: synth bootstrap
	@echo "Deploying infrastructure to LocalStack..."
	cd cdk && cdklocal deploy --all --require-approval never \
		--app "python app.py"

deploy-with-pipeline: synth bootstrap
	@echo "Deploying infrastructure with pipeline to LocalStack..."
	cd cdk && ENABLE_PIPELINE=true cdklocal deploy --all --require-approval never \
		--app "python app.py"

localstack-start:
	@echo "Starting LocalStack..."
	python localstack_setup.py start

localstack-stop:
	@echo "Stopping LocalStack..."
	python localstack_setup.py stop

build-upload:
	@echo "Building and uploading artifacts..."
	python build_and_upload.py

simulate-pipeline:
	@echo "Simulating CI/CD pipeline run..."
	python simulate_pipeline.py simulate-pipeline

list-artifacts:
	@echo "Listing artifacts in the bucket..."
	python access_artifacts.py list-pipelines
	python access_artifacts.py list-final-artifacts

clean:
	@echo "Cleaning build artifacts..."
	rm -rf cdk/cdk.out dist build *.spec
	@echo "Cleaned build artifacts"
