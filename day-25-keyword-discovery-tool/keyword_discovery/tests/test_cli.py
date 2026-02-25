import json
from pathlib import Path
from keyword_discovery.cli import main


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