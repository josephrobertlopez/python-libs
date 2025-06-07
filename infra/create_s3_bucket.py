#!/usr/bin/env python3

import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# S3 bucket name
BUCKET_NAME = "python-libs-artifacts-dev"

# Configure LocalStack endpoint
endpoint_url = "http://localhost:4566"

# Create S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=endpoint_url,
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

# Check if bucket exists
try:
    s3_client.head_bucket(Bucket=BUCKET_NAME)
    print(f"Bucket '{BUCKET_NAME}' already exists")
except Exception:
    # Create bucket
    print(f"Creating bucket '{BUCKET_NAME}'...")
    s3_client.create_bucket(Bucket=BUCKET_NAME)
    
    # Enable versioning
    s3_client.put_bucket_versioning(
        Bucket=BUCKET_NAME,
        VersioningConfiguration={'Status': 'Enabled'}
    )
    
    print(f"Bucket '{BUCKET_NAME}' created successfully with versioning enabled")

# Upload a test file
test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
if os.path.exists(test_file_path):
    s3_key = "test/README.md"
    print(f"Uploading {test_file_path} to s3://{BUCKET_NAME}/{s3_key}")
    with open(test_file_path, 'rb') as file_data:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=file_data)
    print(f"File uploaded successfully")
else:
    print(f"Test file {test_file_path} not found")

# List objects in bucket
print(f"\nListing objects in bucket '{BUCKET_NAME}'...")
response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
for obj in response.get('Contents', []):
    print(f"- {obj['Key']} ({obj['Size']} bytes)")

if not response.get('Contents'):
    print("No objects found in bucket")
