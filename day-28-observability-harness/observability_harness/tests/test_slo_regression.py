from observability_harness.slo.evaluator import evaluate_slo
from observability_harness.slo.types import RequestObservation, SLOSpec


def test_slo_failure_on_degraded_data():
    spec = SLOSpec(
        service="api",
        availability=0.99,
        p95_latency_ms=200,
        error_rate=0.01,
        window_minutes=5,
    )

    observations = [
        RequestObservation(timestamp=100, latency_ms=100, success=True),
        RequestObservation(timestamp=101, latency_ms=100, success=False),
    ]

    result = evaluate_slo(
        observations,
        spec,
        current_time=200,
    )

    assert result.availability_pass is False
    assert "availability" in result.violated