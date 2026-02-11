import json
from pathlib import Path
from src.cli import main


def test_cli_add_list_outcome_stats_json(capsys, tmp_path: Path):
    decision_file = tmp_path / "decisions.json"
    outcome_file = tmp_path / "outcomes.json"
    input_file = tmp_path / "input.json"

    # Create input JSON file
    input_file.write_text(json.dumps({"x": 1}))

    # -----------------
    # Add decision
    # -----------------
    main([
        "--storage-path", str(decision_file),
        "add",
        "--actor", "alice",
        "--title", "CLI test",
        "--description", "testing integration",
        "--context", "unit test",
        "--inputs-file", str(input_file),
    ])

    # Clear stdout from "Recorded decision ..."
    capsys.readouterr()

    # -----------------
    # List decisions (JSON)
    # -----------------
    main([
        "--storage-path", str(decision_file),
        "list",
        "--json",
    ])

    captured = capsys.readouterr()
    decisions_data = json.loads(captured.out.strip())

    assert len(decisions_data) == 1
    decision_id = decisions_data[0]["decision_id"]

    # -----------------
    # Add outcome
    # -----------------
    main([
        "--storage-path", str(decision_file),
        "add-outcome",
        "--decision-id", decision_id,
        "--outcome", "Success",
        "--outcome-storage-path", str(outcome_file),
    ])

    # Clear stdout from outcome confirmation
    capsys.readouterr()

    assert outcome_file.exists()
    outcomes_data = json.loads(outcome_file.read_text())
    assert len(outcomes_data) == 1
    assert outcomes_data[0]["outcome"] == "Success"

    # -----------------
    # Stats (JSON)
    # -----------------
    main([
        "--storage-path", str(decision_file),
        "stats",
        "--outcome-storage-path", str(outcome_file),
        "--json",
    ])

    captured_stats = capsys.readouterr()
    stats_data = json.loads(captured_stats.out.strip())

    assert stats_data["total_decisions"] == 1
    assert stats_data["total_outcomes"] == 1
    assert stats_data["by_actor"]["alice"] == 1
