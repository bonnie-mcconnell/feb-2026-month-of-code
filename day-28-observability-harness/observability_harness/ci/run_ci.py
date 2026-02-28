# observability_harness/ci/run_ci.py
from pathlib import Path
import subprocess
import sys

from .coverage_gate import enforce_coverage
from .schema_validator import validate_slo_yaml
from .docker_gate import verify_docker_build

def main() -> None:
    # Run tests with coverage
    result = subprocess.run(
        ["pytest", "--cov=observability_harness", "--cov-report=xml"],
    )
    if result.returncode != 0:
        sys.exit(result.returncode)

    # Enforce coverage threshold
    enforce_coverage(90.0, Path("coverage.xml"))

    # Validate example SLO YAMLs (optional, if you provide SLO YAMLs in examples)
    example_slo = Path("examples/crypto_arb_integration/example_slo.yaml")
    if example_slo.exists():
        validate_slo_yaml(example_slo)

    # Docker build verification
    try:
        verify_docker_build()
    except SystemExit:
        print("Docker build verification failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()