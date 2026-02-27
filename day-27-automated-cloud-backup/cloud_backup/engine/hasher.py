import hashlib
import os


class HashingError(Exception):
    pass


def sha256_file(path: str, chunk_size: int = 1024 * 1024) -> str:
    """
    Stream file and return SHA-256 hex digest.
    """

    if not os.path.exists(path):
        raise HashingError(f"File does not exist: {path}")

    hasher = hashlib.sha256()

    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
    except PermissionError as e:
        raise HashingError(f"Permission denied: {path}") from e
    except OSError as e:
        raise HashingError(f"IO error hashing {path}: {e}") from e

    return hasher.hexdigest()