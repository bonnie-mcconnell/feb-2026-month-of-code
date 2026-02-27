import os
import shutil
from typing import List

from cloud_backup.storage.base_adapter import BaseStorageAdapter, StorageError


class LocalStorageAdapter(BaseStorageAdapter):
    def __init__(self, destination_root: str):
        self.destination_root = os.path.abspath(destination_root)
        self.objects_root = os.path.join(self.destination_root, "objects")

        os.makedirs(self.objects_root, exist_ok=True)

    # -------------------------

    def upload(self, local_path: str, destination_key: str) -> None:
        dest_path = self._resolve_path(destination_key)

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        try:
            shutil.copy2(local_path, dest_path)
        except Exception as e:
            raise StorageError(f"Upload failed: {destination_key}") from e

    def delete(self, key: str) -> None:
        path = self._resolve_path(key)

        if not os.path.exists(path):
            return

        try:
            os.remove(path)
        except Exception as e:
            raise StorageError(f"Delete failed: {key}") from e

    def exists(self, key: str) -> bool:
        return os.path.exists(self._resolve_path(key))

    def list(self, prefix: str = "") -> List[str]:
        base = self._resolve_path(prefix)

        if not os.path.exists(base):
            return []

        keys = []

        for root, _, files in os.walk(base):
            for name in files:
                full_path = os.path.join(root, name)
                rel = os.path.relpath(full_path, self.objects_root)
                keys.append(rel.replace("\\", "/"))

        return keys

    # -------------------------

    def _resolve_path(self, key: str) -> str:
        normalized = key.replace("/", os.sep)
        return os.path.join(self.objects_root, normalized)