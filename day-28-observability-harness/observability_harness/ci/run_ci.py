from pathlib import Path
import subprocess
import sys
import json

from .coverage_gate import enforce_coverage
from .schema_validator import validate_slo_yaml, validate_log_record
from .docker_gate import verify_docker_build


def main() -> None:
    """
    CI enforcement for the Observability Harness.
    Performs:
      - Test execution with coverage
      - Coverage threshold enforcement
      - Optional SLO YAML validation
      - Docker build integrity check
    """
    # Run tests with coverage
    result = subprocess.run(
        ["pytest", "--cov=observability_harness", "--cov-report=xml"]
    )
    if result.returncode != 0:
        sys.exit(result.returncode)

    # Enforce coverage threshold
    enforce_coverage(90.0, Path("coverage.xml"))

    # Optional: validate log schema
    log_file = Path("tests/fixtures/log_example.json")
    if log_file.exists():
        print("Validating example log record...")
        validate_log_record(json.loads(log_file.read_text()))

    # Optional SLO YAML validation (example YAML if exists)
    example_slo = Path("examples/crypto_arb_integration/example_slo.yaml")
    if example_slo.exists():
        print("Validating example SLO YAML...")
        validate_slo_yaml(example_slo)

    # Docker build verification
    try:
        print("Verifying Docker build...")
        verify_docker_build()
    except SystemExit:
        print("Docker build verification failed.")
        sys.exit(1)

    print("CI checks passed successfully.")


if __name__ == "__main__":
    main()