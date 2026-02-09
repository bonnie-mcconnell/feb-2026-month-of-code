import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "sample_transcript.txt"
GOLDEN = ROOT / "tests" / "golden_output.txt"


def test_cli_text_output_matches_golden():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(SAMPLE),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    # Normalize for trailing periods & whitespace
    def normalize(text: str) -> str:
        return "\n".join(line.rstrip(".").rstrip() for line in text.splitlines())
    
    expected = normalize(GOLDEN.read_text(encoding="utf-8-sig"))
    actual = normalize(result.stdout)
    assert actual == expected