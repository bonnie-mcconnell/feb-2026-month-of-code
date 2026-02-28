import pytest
from instrumentation.retry import retry


def test_retry_raises_after_exhaustion():
    def always_fail():
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        retry(always_fail, retries=2, sleep_fn=lambda x: None)


def test_retry_single_attempt_success():
    def ok():
        return 1

    result = retry(ok, retries=1, sleep_fn=lambda x: None)
    assert result == 1