import os
import boto3
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
bucket_name = os.getenv('S3_BUCKET_NAME')

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# def list_s3_audio_files():
#     response = s3_client.list_objects_v2(Bucket=bucket_name)
#     return [obj['Key'] for obj in response.get('Contents', [])
#             if obj['Key'].lower().endswith(('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'))]

# def download_s3_file(key, dest_path):
#     s3_client.download_file(bucket_name, key, dest_path)

import boto3
from datetime import datetime
import os


def list_s3_audio_files(bucket_name):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name)
    return [obj['Key'] for obj in response.get('Contents', [])]

def download_s3_file(bucket_name, s3_key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, s3_key, local_path)

# def upload_to_s3(bucket_name, local_path, s3_key):
#     s3 = boto3.client('s3')
#     s3.upload_file(local_path, bucket_name, s3_key)

# def upload_to_s3(bucket_name, local_path, user_email=None):
#     """Upload a file to S3 with automatically generated key"""
#     # Generate a unique key
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = os.path.basename(local_path)
    
#     # Create user folder if email provided
#     user_folder = "unknown_user"
#     if user_email:
#         user_folder = user_email.split("@")[0]  # Use the part before @ in email
    
#     s3_key = f"recordings/{user_folder}/{timestamp}_{filename}"
    
#     # Upload the file
#     s3 = boto3.client('s3')
#     try:
#         s3.upload_file(local_path, bucket_name, s3_key)
#         return True, s3_key
#     except Exception as e:
#         return False, str(e)

def upload_to_s3(bucket_name, local_path, s3_key=None, user_email=None):
    """Upload a file to S3 with automatically generated key if not provided"""
    # Generate a unique key if not provided
    if s3_key is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(local_path)
        
        # Create user folder if email provided
        user_folder = "unknown_user"
        if user_email:
            user_folder = user_email.split("@")[0]  # Use the part before @ in email
        
        s3_key = f"recordings/{user_folder}/{timestamp}_{filename}"
    
    # Upload the file
    s3 = boto3.client('s3')
    try:
        s3.upload_file(local_path, bucket_name, s3_key)
        return True, s3_key
    except Exception as e:
        return False, str(e)