from pathlib import Path
import subprocess
import sys

from ci.coverage_gate import enforce_coverage


def main() -> None:
    # Run tests with coverage
    result = subprocess.run(
        ["pytest", "--cov=observability_harness", "--cov-report=xml"],
    )

    if result.returncode != 0:
        sys.exit(result.returncode)

    enforce_coverage(90.0, Path("coverage.xml"))


if __name__ == "__main__":
    main()