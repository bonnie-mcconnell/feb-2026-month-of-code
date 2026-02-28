import pytest
from observability_harness.contracts.slo_schema import SLOSpec
from pydantic import ValidationError


def test_valid_slo():
    slo = SLOSpec(
        service="svc",
        window_minutes=5,
        availability=0.99,
        p95_latency_ms=200,
        error_rate=0.01
    )
    assert slo.service == "svc"


def test_invalid_availability():
    with pytest.raises(ValidationError):
        SLOSpec(
            service="svc",
            window_minutes=5,
            availability=1.5,
            p95_latency_ms=200,
            error_rate=0.01
        )


def test_negative_latency():
    with pytest.raises(ValidationError):
        SLOSpec(
            service="svc",
            window_minutes=5,
            availability=0.99,
            p95_latency_ms=-1,
            error_rate=0.01
        )