import pytest

from cloud_backup.infra.retry import retry, RetryExceededError


class CustomError(Exception):
    pass


def test_retry_succeeds_after_failures():
    calls = {"count": 0}

    def fn():
        calls["count"] += 1
        if calls["count"] < 3:
            raise CustomError("fail")
        return "ok"

    result = retry(
        fn,
        max_attempts=3,
        backoff_seconds=0,
        retry_on=(CustomError,),
    )

    assert result == "ok"
    assert calls["count"] == 3


def test_retry_exhausted():
    def fn():
        raise CustomError("fail")

    with pytest.raises(RetryExceededError):
        retry(
            fn,
            max_attempts=2,
            backoff_seconds=0,
            retry_on=(CustomError,),
        )


def test_non_retryable_bubbles():
    def fn():
        raise ValueError("no retry")

    with pytest.raises(ValueError):
        retry(
            fn,
            max_attempts=3,
            backoff_seconds=0,
            retry_on=(CustomError,),
        )