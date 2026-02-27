import os
from typing import Iterator


class ScanError(Exception):
    pass


def scan_directory(source_root: str) -> Iterator[str]:
    """
    Yields relative file paths in deterministic order.
    """

    if not os.path.isdir(source_root):
        raise ScanError(f"Source directory does not exist: {source_root}")

    source_root = os.path.abspath(source_root)

    for root, dirs, files in os.walk(source_root, topdown=True):
        # Prevent following symlinked directories
        dirs[:] = sorted(
            d for d in dirs
            if not os.path.islink(os.path.join(root, d))
        )

        files = sorted(files)

        for name in files:
            full_path = os.path.join(root, name)

            # Skip broken symlinks
            if os.path.islink(full_path) and not os.path.exists(full_path):
                continue

            try:
                rel_path = os.path.relpath(full_path, source_root)
            except Exception:
                continue

            yield rel_path.replace("\\", "/")  # normalize