import boto3
from moto import mock_s3

from cloud_backup.storage.s3_adapter import S3StorageAdapter


@mock_s3
def test_s3_upload_and_exists_and_download():
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket="test-bucket")

    adapter = S3StorageAdapter(bucket="test-bucket")

    # create temp file
    with open("temp.txt", "w") as f:
        f.write("hello")

    adapter.upload("temp.txt", "file.txt")

    assert adapter.exists("file.txt")
    assert adapter.download("file.txt") == b"hello"

    adapter.delete("file.txt")
    assert not adapter.exists("file.txt")