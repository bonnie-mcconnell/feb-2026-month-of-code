from cloud_backup.domain.snapshot import Snapshot


def test_snapshot_to_dict_and_from_dict():
    snap = Snapshot(
        snapshot_id="abc123",
        timestamp=123.456,
        files_backed_up=["b.txt", "a.txt"],
        files_skipped=["c.txt"],
        files_deleted=["d.txt"],
    )

    data = snap.to_dict()

    # Ensure sorting behavior
    assert data["files_backed_up"] == ["a.txt", "b.txt"]

    restored = Snapshot.from_dict(data)

    assert restored.snapshot_id == snap.snapshot_id
    assert restored.timestamp == snap.timestamp
    assert restored.files_backed_up == ["a.txt", "b.txt"]
    assert restored.files_skipped == ["c.txt"]
    assert restored.files_deleted == ["d.txt"]