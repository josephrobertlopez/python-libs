# Makefile for infrastructure management

.PHONY: install deploy synth localstack-start localstack-stop build-upload clean help

help:
	@echo "Available commands:"
	@echo "  install          Install dependencies"
	@echo "  deploy           Deploy infrastructure to LocalStack"
	@echo "  synth            Synthesize CloudFormation template"
	@echo "  localstack-start Start LocalStack container"
	@echo "  localstack-stop  Stop LocalStack container"
	@echo "  build-upload     Build and upload artifacts"
	@echo "  clean            Clean build artifacts"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

synth:
	@echo "Synthesizing CloudFormation template..."
	cd cdk && python -m app

deploy: synth
	@echo "Deploying infrastructure to LocalStack..."
	cd cdk && cdk deploy --all --require-approval never \
		--context aws:region=us-east-1 \
		--context aws:account=000000000000 \
		--context aws:cdk:endpoint-url=http://localhost:4566 \
		--context aws:cdk:aws-cdk:target-region=us-east-1 \
		--context aws:cdk:aws-cdk:target-account=000000000000

localstack-start:
	@echo "Starting LocalStack..."
	python localstack_setup.py start

localstack-stop:
	@echo "Stopping LocalStack..."
	python localstack_setup.py stop

build-upload:
	@echo "Building and uploading artifacts..."
	python build_and_upload.py

clean:
	@echo "Cleaning build artifacts..."
	rm -rf cdk/cdk.out dist build *.spec
	@echo "Cleaned build artifacts"
