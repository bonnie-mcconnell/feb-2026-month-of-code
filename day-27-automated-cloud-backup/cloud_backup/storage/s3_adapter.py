import boto3
from botocore.exceptions import ClientError
from typing import List

from cloud_backup.storage.base_adapter import BaseStorageAdapter, StorageError


class S3StorageAdapter(BaseStorageAdapter):
    def __init__(self, bucket: str, prefix: str = "") -> None:
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self.client = boto3.client("s3")

    # -------------------------

    def _key(self, key: str) -> str:
        if self.prefix:
            return f"{self.prefix}/{key}"
        return key

    # -------------------------

    def upload(self, local_path: str, destination_key: str) -> None:
        try:
            with open(local_path, "rb") as f:
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=self._key(destination_key),
                    Body=f,
                )
        except Exception as e:
            raise StorageError(f"S3 upload failed: {destination_key}") from e

    def delete(self, key: str) -> None:
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=self._key(key),
            )
        except Exception as e:
            raise StorageError(f"S3 delete failed: {key}") from e

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=self._key(key),
            )
            return True
        except ClientError:
            return False

    def list(self, prefix: str = "") -> List[str]:
        full_prefix = self._key(prefix) if prefix else self.prefix

        paginator = self.client.get_paginator("list_objects_v2")
        result: List[str] = []

        for page in paginator.paginate(
            Bucket=self.bucket,
            Prefix=full_prefix,
        ):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if self.prefix:
                    key = key[len(self.prefix) + 1 :]
                result.append(key)

        return sorted(result)

    def download(self, key: str) -> bytes:
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=self._key(key),
            )
            return response["Body"].read()
        except Exception as e:
            raise StorageError(f"S3 download failed: {key}") from e