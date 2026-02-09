import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "src" / "cli.py"
SAMPLE = ROOT / "examples" / "sample_transcript.txt"
GOLDEN = ROOT / "tests" / "golden_output.txt"


def test_cli_text_output_matches_golden():
    result = subprocess.run(
        [sys.executable, str(CLI), str(SAMPLE)],
        capture_output=True,
        text=True,
        check=True,
    )

    expected = GOLDEN.read_text().strip()
    actual = result.stdout.strip()

    assert actual == expected
