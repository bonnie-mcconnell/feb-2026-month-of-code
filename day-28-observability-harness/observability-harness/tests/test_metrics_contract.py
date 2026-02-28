import pytest
from contracts.metrics_contract import MetricRecord
from pydantic import ValidationError


def test_valid_metric():
    m = MetricRecord(
        name="request_count",
        value=1.0,
        labels={"service": "test"}
    )
    assert m.name == "request_count"


def test_uppercase_name_fails():
    with pytest.raises(ValidationError):
        MetricRecord(
            name="Request_Count",
            value=1.0,
            labels={}
        )


def test_space_in_name_fails():
    with pytest.raises(ValidationError):
        MetricRecord(
            name="request count",
            value=1.0,
            labels={}
        )