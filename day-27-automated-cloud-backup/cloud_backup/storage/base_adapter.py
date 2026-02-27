from abc import ABC, abstractmethod
from typing import List


class StorageError(Exception):
    pass


class BaseStorageAdapter(ABC):
    """
    Storage adapter contract.
    Implementations must perform raw IO only.
    No retry. No logging. No business logic.
    """

    @abstractmethod
    def upload(self, local_path: str, destination_key: str) -> None:
        """
        Upload local file to storage.
        Must overwrite if exists.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete object from storage.
        Must not error if key does not exist.
        """

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if object exists.
        """

    @abstractmethod
    def list(self, prefix: str = "") -> List[str]:
        """
        List object keys under prefix.
        Must return relative keys.
        """

    def download(self, key: str) -> bytes:
        raise NotImplementedError