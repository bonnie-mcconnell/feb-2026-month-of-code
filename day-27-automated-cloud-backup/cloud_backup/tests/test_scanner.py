from cloud_backup.engine.scanner import scan_directory


def test_scan_nested_structure(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "file1.txt").write_text("x")
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "file2.txt").write_text("y")

    files = list(scan_directory(str(tmp_path)))

    assert files == sorted(files)
    assert "a/file1.txt" in files
    assert "b/file2.txt" in files


def test_scan_deterministic(tmp_path):
    (tmp_path / "z.txt").write_text("z")
    (tmp_path / "a.txt").write_text("a")

    first = list(scan_directory(str(tmp_path)))
    second = list(scan_directory(str(tmp_path)))

    assert first == second