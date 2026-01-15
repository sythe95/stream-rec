import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv

load_dotenv()

# Common settings
access_key = os.getenv("AWS_ACCESS_KEY_ID", "minio")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "minio123")
bucket_name = "stream-rec-debug"

print(f"🔧 Debugging MinIO Connection...")
print(f"   User: {access_key}")
print(f"   Pass: {secret_key[:3]}***")

def try_connection(name, endpoint, style, region):
    print(f"\n🧪 Attempting Strategy: {name}")
    print(f"   Endpoint: {endpoint} | Style: {style} | Region: {region}")
    
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(s3={'addressing_style': style}, signature_version='s3v4')
        )
        
        # 1. List Buckets (The simplest check)
        print("   > Listing buckets...")
        response = s3.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]
        print(f"   ✅ Success! Buckets found: {buckets}")
        
        # 2. Create Bucket
        if bucket_name not in buckets:
            print(f"   > Creating bucket '{bucket_name}'...")
            # Note: us-east-1 requires NO LocationConstraint
            if region == "us-east-1":
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
            print(f"   ✅ Bucket created!")
            
        # 3. Upload File
        print(f"   > Uploading test file...")
        s3.put_object(Bucket=bucket_name, Key="hello.txt", Body=b"Hello MinIO!")
        print(f"   ✅ Upload success!")
        print(f"   🎉 STRATEGY '{name}' IS THE WINNER!")
        return True

    except Exception as e:
        print(f"   ❌ Failed. Error: {e}")
        return False

# --- STRATEGY 1: The "Localhost" Standard ---
# This is what most docs say to use
if try_connection("Standard Localhost", "http://localhost:9011", "path", "us-east-1"):
    exit(0)

# --- STRATEGY 2: The "IP Address" Direct ---
# Bypasses DNS, often fixes Linux/Docker networking issues
if try_connection("Direct IP", "http://127.0.0.1:9011", "path", "us-east-1"):
    exit(0)

# --- STRATEGY 3: The "Explicit Region" ---
# Sometimes MinIO is accidentally configured with a region
if try_connection("Explicit Region", "http://127.0.0.1:9011", "path", "test-region"):
    exit(0)

print("\n💥 All strategies failed. Please check if MinIO is actually running on port 9011.")