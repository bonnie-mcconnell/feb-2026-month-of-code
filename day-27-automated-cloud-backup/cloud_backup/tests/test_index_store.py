from cloud_backup.engine.index_store import IndexStore
from cloud_backup.domain.file_record import FileRecord
from cloud_backup.domain.snapshot import Snapshot


def test_index_roundtrip(tmp_path):
    index_path = tmp_path / "index.json"
    store = IndexStore(str(index_path))

    files = {
        "file.txt": FileRecord(
            relative_path="file.txt",
            size=10,
            modified_at=1.0,
            sha256="abc",
            last_backup_timestamp=2.0,
        )
    }

    snapshots = [
        Snapshot(
            snapshot_id="snap1",
            timestamp=1.0,
            files_backed_up=["file.txt"],
            files_skipped=[],
            files_deleted=[],
        )
    ]

    store.save(files, snapshots)

    loaded_files, loaded_snaps = store.load()

    assert loaded_files["file.txt"].sha256 == "abc"
    assert loaded_snaps[0].snapshot_id == "snap1"