import pytest
import yaml
from pathlib import Path
from observability_harness.ci.schema_validator import (
    validate_log_record,
    validate_metric_name,
    validate_slo_yaml,
)

def test_validate_metric_name_valid() -> None:
    validate_metric_name("request_count")


def test_invalid_log_missing_field():
    with pytest.raises(Exception):
        validate_log_record({"service": "x"})


def test_invalid_metric_name():
    with pytest.raises(Exception):
        validate_metric_name("not_a_valid_metric")


def test_invalid_yaml_syntax(tmp_path: Path):
    file = tmp_path / "slo.yaml"
    file.write_text("invalid: : yaml")

    with pytest.raises(ValueError):
        validate_slo_yaml(file)


def test_validate_slo_yaml_valid(tmp_path: Path) -> None:
    data = {
        "service": "test",
        "availability": "99%",
        "p95_latency_ms": 200,
        "error_rate": "1%",
        "window_minutes": 5,
    }

    file = tmp_path / "slo.yaml"
    file.write_text(yaml.safe_dump(data))

    validate_slo_yaml(file)


def test_validate_slo_yaml_missing_field(tmp_path: Path) -> None:
    data = {"service": "test"}

    file = tmp_path / "slo.yaml"
    file.write_text(yaml.safe_dump(data))

    with pytest.raises(ValueError):
        validate_slo_yaml(file)