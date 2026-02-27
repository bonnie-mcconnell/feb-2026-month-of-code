import hashlib
import os

from cloud_backup.engine.hasher import sha256_file


def test_same_content_same_hash(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello world")

    h1 = sha256_file(str(f))
    h2 = sha256_file(str(f))

    assert h1 == h2


def test_modified_file_changes_hash(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")

    h1 = sha256_file(str(f))

    f.write_text("hello world")
    h2 = sha256_file(str(f))

    assert h1 != h2


def test_empty_file_hash(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")

    expected = hashlib.sha256(b"").hexdigest()
    assert sha256_file(str(f)) == expected


def test_large_file(tmp_path):
    f = tmp_path / "large.bin"
    f.write_bytes(b"a" * (10 * 1024 * 1024))  # 10MB

    h = sha256_file(str(f))
    assert isinstance(h, str)
    assert len(h) == 64