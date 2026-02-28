import pytest
from pathlib import Path
from ci.schema_validator import (
    validate_log_record,
    validate_metric_name,
    validate_slo_yaml,
)


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


def test_missing_required_slo_fields(tmp_path: Path):
    file = tmp_path / "slo.yaml"
    file.write_text("service: test")

    with pytest.raises(ValueError):
        validate_slo_yaml(file)