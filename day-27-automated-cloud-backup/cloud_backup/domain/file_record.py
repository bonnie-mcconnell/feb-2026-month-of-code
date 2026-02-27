from dataclasses import dataclass


@dataclass(frozen=True)
class FileRecord:
    relative_path: str
    size: int
    modified_at: float
    sha256: str
    last_backup_timestamp: float

    def to_dict(self) -> dict:
        return {
            "size": self.size,
            "modified_at": self.modified_at,
            "sha256": self.sha256,
            "last_backup_timestamp": self.last_backup_timestamp,
        }

    @staticmethod
    def from_dict(relative_path: str, data: dict) -> "FileRecord":
        return FileRecord(
            relative_path=relative_path,
            size=data["size"],
            modified_at=data["modified_at"],
            sha256=data["sha256"],
            last_backup_timestamp=data["last_backup_timestamp"],
        )