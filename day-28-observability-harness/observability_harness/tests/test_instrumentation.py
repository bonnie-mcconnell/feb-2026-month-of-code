import pytest
from observability_harness.instrumentation.logger import StructuredLogger, LogLevel
from observability_harness.instrumentation.timing import timed
from observability_harness.instrumentation.retry import retry
from observability_harness.instrumentation.correlation import CorrelationContext


# -------------------------
# Logger Tests
# -------------------------
def test_logger_creates_valid_record():
    logger = StructuredLogger(service="test", environment="dev")
    ctx = CorrelationContext("cid-123")

    record = logger.log(
        event="test-event",
        level=LogLevel.INFO,
        correlation_id=ctx.correlation_id,
    )

    assert record.service == "test"
    assert record.correlation_id == "cid-123"
    assert record.event == "test-event"
    assert record.level == LogLevel.INFO


# -------------------------
# Timing Tests
# -------------------------
def test_timed_returns_result_and_elapsed():
    def slow_fn():
        return 42

    wrapped = timed(slow_fn)
    result, elapsed = wrapped()

    assert result == 42
    assert isinstance(elapsed, int)
    assert elapsed >= 0


# -------------------------
# Retry Tests (Decorator Style)
# -------------------------
def test_retry_succeeds_after_retries():
    attempts = {"count": 0}

    @retry(attempts=3)
    def flaky():
        if attempts["count"] < 2:
            attempts["count"] += 1
            raise ValueError("fail")
        return "ok"

    result = flaky()
    assert result == "ok"
    assert attempts["count"] == 2


def test_retry_raises_after_exhaustion():
    @retry(attempts=2)
    def always_fail():
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        always_fail()


def test_retry_single_attempt_success():
    @retry(attempts=1)
    def succeed():
        return 1

    assert succeed() == 1


# -------------------------
# Correlation Context Tests
# -------------------------
def test_correlation_context_yields_string_id():
    ctx = CorrelationContext()

    with ctx.use() as cid:
        assert isinstance(cid, str)
        assert len(cid) > 0