import pytest
from decimal import Decimal
from infra.retry import retry, RetryError


class FakeSleep:
    def __init__(self):
        self.calls = []

    def __call__(self, seconds: float):
        self.calls.append(seconds)


def test_retry_immediate_success():
    def fn():
        return 42

    result = retry(
        fn,
        max_attempts=3,
        base_delay=Decimal("1"),
        backoff_multiplier=Decimal("2"),
        retry_on=(ValueError,),
    )

    assert result == 42


def test_retry_then_success():
    attempts = {"count": 0}
    sleep = FakeSleep()

    def fn():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("transient")
        return "ok"

    result = retry(
        fn,
        max_attempts=5,
        base_delay=Decimal("1"),
        backoff_multiplier=Decimal("2"),
        retry_on=(ValueError,),
        sleep_func=sleep,
    )

    assert result == "ok"
    assert sleep.calls == [1.0, 2.0]


def test_retry_exhausts_and_raises():
    sleep = FakeSleep()

    def fn():
        raise ValueError("fail")

    try:
        retry(
            fn,
            max_attempts=3,
            base_delay=Decimal("1"),
            backoff_multiplier=Decimal("2"),
            retry_on=(ValueError,),
            sleep_func=sleep,
        )
    except RetryError:
        pass
    else:
        assert False, "Expected RetryError"

    assert sleep.calls == [1.0, 2.0]


def test_non_retryable_exception_bubbles():
    def fn():
        raise RuntimeError("fatal")

    try:
        retry(
            fn,
            max_attempts=3,
            base_delay=Decimal("1"),
            backoff_multiplier=Decimal("2"),
            retry_on=(ValueError,),
        )
    except RuntimeError:
        pass
    else:
        assert False, "Expected RuntimeError"


def test_invalid_parameters():
    with pytest.raises(ValueError):
        retry(lambda: 1, max_attempts=0,
              base_delay=Decimal("1"),
              backoff_multiplier=Decimal("2"),
              retry_on=(ValueError,))

    with pytest.raises(ValueError):
        retry(lambda: 1, max_attempts=3,
              base_delay=Decimal("0"),
              backoff_multiplier=Decimal("2"),
              retry_on=(ValueError,))

    with pytest.raises(ValueError):
        retry(lambda: 1, max_attempts=3,
              base_delay=Decimal("1"),
              backoff_multiplier=Decimal("0.5"),
              retry_on=(ValueError,))