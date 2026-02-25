import pytest
import json
from keyword_discovery.cli import main


def test_cli_basic(tmp_path, monkeypatch, capsys):
    file = tmp_path / "doc.txt"
    file.write_text("alpha beta beta", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["keyword-discover", "--input", str(tmp_path), "--top", "1"],
    )

    from keyword_discovery.cli import main
    main()

    out = capsys.readouterr().out
    data = json.loads(out)

    assert "top_keywords" in data
    assert len(data["top_keywords"]) == 1


def test_cli_export(tmp_path, monkeypatch):
    file = tmp_path / "doc.txt"
    file.write_text("alpha beta beta", encoding="utf-8")

    export = tmp_path / "out.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "keyword-discover",
            "--input",
            str(tmp_path),
            "--export",
            str(export),
        ],
    )

    from keyword_discovery.cli import main
    main()

    assert export.exists()


def test_cli_invalid_path(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["keyword-discover", "--input", "nonexistent_dir"],
    )

    from keyword_discovery.cli import main

    with pytest.raises(SystemExit):
        main()


def test_cli_outputs_json(tmp_path, monkeypatch, capsys):
    file = tmp_path / "doc.txt"
    file.write_text("alpha beta beta", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "keyword-discover",
            "--input",
            str(tmp_path),
            "--top",
            "1",
        ],
    )

    main()

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert "top_keywords" in data
    assert len(data["top_keywords"]) == 1