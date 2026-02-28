from pathlib import Path
from typing import Any, Dict

import yaml

from observability_harness.contracts.logging_schema import LogRecord
from observability_harness.contracts.metrics_contract import (
    MetricRecord,
)


def validate_log_record(record: Dict[str, Any]) -> None:
    """
    Validate that a log record conforms to LogRecord schema.
    Raises ValidationError on failure.
    """
    LogRecord(**record)


def validate_metric_name(name: str) -> None:
    """
    Validate that a metric name is allowed by attempting to construct
    a MetricRecord using the declared Literal contract.
    """
    MetricRecord(
        name=name,  # type: ignore[arg-type]
        value=1.0,
    )


def validate_slo_yaml(path: Path) -> None:
    """
    Validate that SLO YAML file is syntactically valid and contains required keys.
    """
    if not path.exists():
        raise ValueError("SLO YAML file not found.")

    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("SLO YAML must define a mapping.")

    required = {
        "service",
        "availability",
        "p95_latency_ms",
        "error_rate",
        "window_minutes",
    }

    missing = required - set(data.keys())

    if missing:
        raise ValueError(f"SLO YAML missing required fields: {missing}")