import json
from pathlib import Path
import tempfile

from src.cli import main


def test_cli_add_and_list_json(tmp_path: Path):
    decision_file = tmp_path / "decisions.json"

    # Add a decision via CLI
    main([
        "--storage-path", str(decision_file),
        "add",
        "--actor", "alice",
        "--title", "CLI test",
        "--description", "testing integration",
        "--context", "unit test",
        "--inputs", '{"x": 1}'
    ])

    assert decision_file.exists()

    raw = decision_file.read_text()
    data = json.loads(raw)
    assert len(data) == 1
    assert data[0]["actor"] == "alice"

    # Capture JSON list output
    # Instead of capturing stdout manually, we re-load file
    main([
        "--storage-path", str(decision_file),
        "list",
        "--json",
    ])

    # Ensure still only one record
    raw_after = decision_file.read_text()
    data_after = json.loads(raw_after)
    assert len(data_after) == 1
