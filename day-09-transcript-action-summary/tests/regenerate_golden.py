# tests/regenerate_golden.py
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
SAMPLE = ROOT.parent / "examples" / "sample_transcript.txt"
GOLDEN = ROOT / "golden_output.txt"

# Run your CLI and capture stdout
result = subprocess.run(
    ["python", "-m", "src.cli", str(SAMPLE), "--segments"],  # add any flags your test uses
    capture_output=True,
    text=True,  # makes stdout a string, not bytes
    check=True,
)

# Write to golden file in UTF-8
GOLDEN.write_text(result.stdout, encoding="utf-8")
print(f"Golden file regenerated at {GOLDEN}")
