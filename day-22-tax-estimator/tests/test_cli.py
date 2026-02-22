import sys
from pathlib import Path

import pytest

from tax_engine.cli.main import main


def test_cli_estimate_runs(monkeypatch, tmp_path):
    # Use an existing jurisdiction config in your project
    config_dir = Path("config/jurisdictions")
    sample = next(config_dir.glob("*.json"))

    jurisdiction_name = sample.stem

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--jurisdiction",
            jurisdiction_name,
            "--income",
            "100000",
        ],
    )

    main()  # should not raise


def test_cli_simulation_runs(monkeypatch):
    config_dir = Path("config/jurisdictions")
    sample = next(config_dir.glob("*.json"))

    jurisdiction_name = sample.stem

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--jurisdiction",
            jurisdiction_name,
            "--simulate",
            "10000",
            "20000",
            "5000",
        ],
    )

    main()  # should not raise