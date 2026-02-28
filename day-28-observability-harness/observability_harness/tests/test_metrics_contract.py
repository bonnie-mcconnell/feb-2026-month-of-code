import pytest
from pydantic import ValidationError
from contracts.metrics_contract import MetricRecord


def test_valid_metric():
    m = MetricRecord(
        name="request_count",
        value=10,
        labels={"service": "api"}
    )
    assert m.name == "request_count"


def test_invalid_metric_name():
    with pytest.raises(ValidationError):
        MetricRecord(
            name="unknown_metric", # type: ignore
            value=1,
            labels={}
        )


def test_negative_value():
    with pytest.raises(ValidationError):
        MetricRecord(
            name="request_count",
            value=-1,
            labels={}
        )


def test_invalid_suffix():
    with pytest.raises(ValidationError):
        MetricRecord(
            name="custom_ms", # type: ignore
            value=10,
            labels={}
        )


def test_too_many_labels():
    labels = {f"k{i}": "v" for i in range(11)}
    with pytest.raises(ValidationError):
        MetricRecord(
            name="request_count",
            value=1,
            labels=labels
        )


def test_uppercase_label_key():
    with pytest.raises(ValidationError):
        MetricRecord(
            name="request_count",
            value=1,
            labels={"Service": "api"}
        )