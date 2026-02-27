import os
import tempfile

from cloud_backup.storage.local_adapter import LocalStorageAdapter


def test_upload_and_exists_and_download():
    with tempfile.TemporaryDirectory() as tmp:
        adapter = LocalStorageAdapter(tmp)

        file_path = os.path.join(tmp, "source.txt")
        with open(file_path, "w") as f:
            f.write("hello")

        adapter.upload(file_path, "backup/source.txt")

        assert adapter.exists("backup/source.txt")

        data = adapter.download("backup/source.txt")
        assert data == b"hello"


def test_delete():
    with tempfile.TemporaryDirectory() as tmp:
        adapter = LocalStorageAdapter(tmp)

        file_path = os.path.join(tmp, "file.txt")
        with open(file_path, "w") as f:
            f.write("data")

        adapter.upload(file_path, "file.txt")
        assert adapter.exists("file.txt")

        adapter.delete("file.txt")
        assert not adapter.exists("file.txt")


def test_list():
    with tempfile.TemporaryDirectory() as tmp:
        adapter = LocalStorageAdapter(tmp)

        for name in ["a.txt", "b.txt"]:
            path = os.path.join(tmp, name)
            with open(path, "w") as f:
                f.write(name)
            adapter.upload(path, name)

        files = adapter.list()
        assert sorted(files) == ["a.txt", "b.txt"]