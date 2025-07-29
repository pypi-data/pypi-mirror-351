from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from baresquare_sdk.core import logger


class S3Client:
    def __init__(self):
        self.client = boto3.client("s3")

    def download_file(self, bucket: str, key: str, local_path: Path) -> bool:
        """Download a file from S3 to a local path.
        Returns True if successful, False otherwise.
        """
        try:
            self.client.download_file(bucket, key, str(local_path))
            return True
        except ClientError as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            return False

    def upload_file(self, local_path: Path, bucket: str, key: str) -> bool:
        """Upload a file to S3 from a local path.
        Returns True if successful, False otherwise.
        """
        try:
            self.client.upload_file(str(local_path), bucket, key)
            return True
        except ClientError as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return False
