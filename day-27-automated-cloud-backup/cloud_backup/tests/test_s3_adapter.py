import boto3
from moto import mock_aws

from cloud_backup.storage.s3_adapter import S3StorageAdapter


def test_s3_upload_list_exists_download_delete(tmp_path):
    with mock_aws():
        # Setup fake S3
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        adapter = S3StorageAdapter(bucket="test-bucket")

        # Create file to upload
        file_path = tmp_path / "hello.txt"
        file_path.write_text("hello world")

        # Upload
        adapter.upload(str(file_path), "folder/hello.txt")

        # Exists
        assert adapter.exists("folder/hello.txt")

        # List
        keys = adapter.list()
        assert "folder/hello.txt" in keys

        # Download
        data = adapter.download("folder/hello.txt")
        assert data == b"hello world"

        # Delete
        adapter.delete("folder/hello.txt")
        assert not adapter.exists("folder/hello.txt")