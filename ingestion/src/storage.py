import os

import boto3
from botocore.client import Config


class MinioStorage:
    def __init__(self):
        endpoint = os.environ["MINIO_ENDPOINT"]
        access_key = os.environ["MINIO_ACCESS_KEY"]
        secret_key = os.environ["MINIO_SECRET_KEY"]
        self.bucket = os.environ["MINIO_BUCKET"]

        self.client = boto3.client(
            "s3",
            endpoint_url=f"http://{endpoint}",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    def ensure_bucket(self):
        buckets = self.client.list_buckets()["Buckets"]

        existing = {
            bucket["Name"]
            for bucket in buckets
        }

        if self.bucket not in existing:
            self.client.create_bucket(
                Bucket=self.bucket
            )

    def upload_file(
            self,
            local_path: str,
            object_key: str,
    ):
        self.client.upload_file(
            local_path,
            self.bucket,
            object_key,
        )

        return f"s3://{self.bucket}/{object_key}"
