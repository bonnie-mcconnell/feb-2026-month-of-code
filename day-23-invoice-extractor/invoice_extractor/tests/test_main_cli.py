import subprocess
import sys
from pathlib import Path


FIXTURE = Path("tests/fixtures/sample_invoice_1.pdf")


def test_cli_json_output() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "invoice_extractor.main", str(FIXTURE), "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert '"invoice_number"' in result.stdout

