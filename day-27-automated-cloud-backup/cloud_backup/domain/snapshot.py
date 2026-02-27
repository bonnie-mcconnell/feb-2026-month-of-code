from dataclasses import dataclass


@dataclass(frozen=True)
class Snapshot:
    snapshot_id: str
    timestamp: float
    files_backed_up: list[str]
    files_skipped: list[str]
    files_deleted: list[str]

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "files_backed_up": sorted(self.files_backed_up),
            "files_skipped": sorted(self.files_skipped),
            "files_deleted": sorted(self.files_deleted),
        }

    @staticmethod
    def from_dict(data: dict) -> "Snapshot":
        return Snapshot(
            snapshot_id=data["snapshot_id"],
            timestamp=data["timestamp"],
            files_backed_up=list(data["files_backed_up"]),
            files_skipped=list(data["files_skipped"]),
            files_deleted=list(data["files_deleted"]),
        )