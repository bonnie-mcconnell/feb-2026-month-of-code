from pathlib import Path
from invoice_extractor.main import main
import sys


def test_main_json_output(monkeypatch, capsys, tmp_path) -> None:
    # create dummy PDF path that triggers FileNotFoundError
    test_args = ["prog", "nonexistent.pdf", "--json"]

    monkeypatch.setattr(sys, "argv", test_args)

    try:
        main()
    except SystemExit:
        pass

    captured = capsys.readouterr()

    assert "File not found" in captured.err