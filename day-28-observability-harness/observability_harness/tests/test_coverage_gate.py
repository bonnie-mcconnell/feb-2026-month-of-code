import pytest
from pathlib import Path
from observability_harness.ci.coverage_gate import enforce_coverage


def write_xml(path: Path, rate: float) -> None:
    path.write_text(f'<coverage line-rate="{rate}"></coverage>')


def test_fails_below_threshold(tmp_path: Path):
    file = tmp_path / "coverage.xml"
    write_xml(file, 0.85)

    with pytest.raises(SystemExit):
        enforce_coverage(90.0, file)


def test_passes_above_threshold(tmp_path: Path):
    file = tmp_path / "coverage.xml"
    write_xml(file, 0.95)

    enforce_coverage(90.0, file)


def test_malformed_xml(tmp_path: Path):
    file = tmp_path / "coverage.xml"
    file.write_text("<coverage>")

    with pytest.raises(SystemExit):
        enforce_coverage(90.0, file)


def test_coverage_gate_failure(tmp_path: Path) -> None:
    file = tmp_path / "coverage.xml"
    file.write_text(
        """<?xml version="1.0" ?>
        <coverage line-rate="0.5"></coverage>
        """
    )

    with pytest.raises(SystemExit):
        enforce_coverage(90.0, file)