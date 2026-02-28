from observability_harness.instrumentation.logger import (
    StructuredLogger,
    emit_log,
)
from observability_harness.contracts.logging_schema import LogLevel
from observability_harness.instrumentation.retry import retry
from observability_harness.chaos.injectors import (
    maybe_inject_latency,
    maybe_inject_exception,
)
from observability_harness.chaos.toggles import ChaosConfig
from observability_harness.slo.evaluator import evaluate_slo
from observability_harness.slo.types import (
    RequestObservation,
    SLOSpec,
)

from dataclasses import asdict

def test_logging():
    """Validates logging functionality including StructuredLogger and emit_log."""
    print("\n=== Logging Validation ===")

    logger = StructuredLogger(service="manual-service", environment="dev")

    record = logger.log(
        event="manual_test_event",
        level=LogLevel.INFO,
        correlation_id="abc-123",
        latency_ms=150,
        metadata={"feature": "manual"},
    )

    print("StructuredLogger OK:", record.model_dump())

    record2 = emit_log(
        service="manual-service",
        environment="dev",
        level=LogLevel.ERROR,
        correlation_id="xyz-999",
        event="emit_log_event",
        error_type="ValueError",
    )

    print("emit_log OK:", record2.model_dump())

    # negative test
    try:
        logger.log(
            event="bad_latency",
            level=LogLevel.INFO,
            correlation_id="abc",
            latency_ms=-5,  # should fail
        )
    except Exception as e:
        print("Correctly rejected invalid latency:", type(e).__name__)


def test_retry():
    print("\n=== Retry Validation ===")

    counter = {"n": 0}

    @retry(attempts=3)
    def flaky():
        counter["n"] += 1
        if counter["n"] < 3:
            raise ValueError("fail")
        return "success"

    result = flaky()
    print("Retry result:", result)

    # failure case
    counter2 = {"n": 0}

    @retry(attempts=2)
    def always_fail():
        counter2["n"] += 1
        raise RuntimeError("boom")

    try:
        always_fail()
    except RuntimeError:
        print("Retry correctly raised after max attempts")

def test_chaos():
    print("\n=== Chaos Validation ===")

    chaos = ChaosConfig(
        enabled=True,
        inject_latency_ms=100,
        force_exception=False,
        simulate_disk_failure=False,
        simulate_timeout=False,
    )

    def my_fn():
        return "OK"

    def fake_sleep(ms):
        print(f"Sleeping for {ms}ms")

    result = maybe_inject_latency(
        my_fn,
        chaos=chaos,
        sleep_fn=fake_sleep,
    )

    print("Latency injection result:", result)

    chaos2 = ChaosConfig(
        enabled=True,
        inject_latency_ms=None,
        force_exception=True,
        simulate_disk_failure=False,
        simulate_timeout=False,
    )

    try:
        maybe_inject_exception(
            my_fn,
            chaos=chaos2,
            exception_factory=lambda: ValueError("Injected"),
        )
    except ValueError:
        print("Exception injection worked")


def test_slo():
    print("\n=== SLO Evaluation ===")

    observations = [
        RequestObservation(timestamp=1000, latency_ms=100, success=True),
        RequestObservation(timestamp=1010, latency_ms=200, success=True),
        RequestObservation(timestamp=1020, latency_ms=300, success=False),
    ]

    spec = SLOSpec(
        service="manual-service",
        window_minutes=5,
        availability=0.5,
        p95_latency_ms=500,
        error_rate=0.5,
    )

    result = evaluate_slo(
        observations,
        spec,
        current_time=1025,
    )

    print("SLO Result:", asdict(result))


if __name__ == "__main__":
    test_logging()
    test_retry()
    test_chaos()
    test_slo()