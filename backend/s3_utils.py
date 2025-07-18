import os
import boto3
from dotenv import load_dotenv
from datetime import datetime

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


def list_s3_audio_files(bucket_name):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name)
    return [obj['Key'] for obj in response.get('Contents', [])]

def download_s3_file(bucket_name, s3_key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, s3_key, local_path)

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

def upload_custom_file_to_s3(bucket_name, local_file_path, user_email=None):

    # Generate a unique key for the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(local_file_path)
    
    # Define user folder based on email
    user_folder = "unknown_user"
    if user_email:
        user_folder = user_email.split("@")[0]
    
    # Create the S3 key path
    s3_key = f"custom_uploads/{user_folder}/{timestamp}_{filename}"
    
    # Initialize S3 client
    s3 = boto3.client('s3')
    try:
        # Upload file
        s3.upload_file(local_file_path, bucket_name, s3_key)
        return True, s3_key
    except Exception as e:
        return False, str(e)