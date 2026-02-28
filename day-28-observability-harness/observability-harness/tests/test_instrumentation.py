import pytest
from instrumentation.logger import StructuredLogger
from instrumentation.timing import timed
from instrumentation.retry import retry
from instrumentation.correlation import CorrelationContext

def test_logger_creates_valid_record():
    logger = StructuredLogger(service="test", environment="dev")
    ctx = CorrelationContext("cid-123")
    record = logger.log("test-event", "INFO", ctx.correlation_id)
    assert record.service == "test"
    assert record.correlation_id == "cid-123"

def test_timed_returns_elapsed():
    def slow_fn():
        return 42
    fn = timed(slow_fn)
    result, elapsed = fn()
    assert result == 42
    assert isinstance(elapsed, int)
    assert elapsed >= 0

def test_retry_success_after_attempts():
    attempts = []
    def flaky():
        if len(attempts) < 2:
            attempts.append(1)
            raise ValueError("fail")
        return "ok"
    res = retry(flaky, retries=3, sleep_fn=lambda x: None)
    assert res == "ok"
    assert len(attempts) == 2

def test_correlation_context_yields_id():
    ctx = CorrelationContext()
    with ctx.use() as cid:
        assert isinstance(cid, str)