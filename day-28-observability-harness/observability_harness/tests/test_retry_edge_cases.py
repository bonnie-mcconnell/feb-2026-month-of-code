import pytest
from observability_harness.instrumentation.retry import retry


def test_retry_raises_after_exhaustion():
    @retry(attempts=2)
    def always_fail():
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        always_fail()


def test_retry_single_attempt_success():
    @retry(attempts=1)
    def ok():
        return 1

    assert ok() == 1