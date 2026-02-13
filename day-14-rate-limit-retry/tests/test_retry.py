import pytest

from src.retry import RetryPolicy
from src.exceptions import RetryableError, FatalError


def test_retries_until_success():
    calls = {"count": 0}
    sleeps = []

    def fake_sleep(delay):
        sleeps.append(delay)

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RetryableError("temporary")
        return "ok"

    policy = RetryPolicy(
        max_attempts=5,
        base_delay=1,
        sleep_fn=fake_sleep,
    )

    wrapped = policy(flaky)
    result = wrapped()

    assert result == "ok"
    assert calls["count"] == 3
    assert policy.last_attempt_count == 3
    assert policy.last_retry_count == 2
    assert policy.last_total_wait == sum(sleeps)


def test_stops_at_max_attempts():
    calls = {"count": 0}
    sleeps = []

    def fake_sleep(delay):
        sleeps.append(delay)

    def always_fail():
        calls["count"] += 1
        raise RetryableError("still failing")

    policy = RetryPolicy(
        max_attempts=3,
        base_delay=1,
        sleep_fn=fake_sleep,
    )

    wrapped = policy(always_fail)

    with pytest.raises(RetryableError):
        wrapped()

    assert calls["count"] == 3
    assert policy.last_attempt_count == 3
    assert policy.last_retry_count == 2
    assert len(sleeps) == 2


def test_backoff_increases_exponentially():
    sleeps = []

    def fake_sleep(delay):
        sleeps.append(delay)

    def fail():
        raise RetryableError("fail")

    policy = RetryPolicy(
        max_attempts=4,
        base_delay=1,
        backoff_factor=2,
        sleep_fn=fake_sleep,
    )

    wrapped = policy(fail)

    with pytest.raises(RetryableError):
        wrapped()

    assert sleeps == [1, 2, 4]


def test_jitter_within_bounds():
    sleeps = []

    def fake_sleep(delay):
        sleeps.append(delay)

    def fixed_random():
        return 0.5

    def fail():
        raise RetryableError("fail")

    policy = RetryPolicy(
        max_attempts=3,
        base_delay=2,
        backoff_factor=2,
        jitter=True,
        sleep_fn=fake_sleep,
        random_fn=fixed_random,
    )

    wrapped = policy(fail)

    with pytest.raises(RetryableError):
        wrapped()

    # expected base delays: 2, 4
    # jittered with 0.5 multiplier → 1, 2
    assert sleeps == [1.0, 2.0]


def test_fatal_error_not_retried():
    calls = {"count": 0}

    def fail_fatal():
        calls["count"] += 1
        raise FatalError("bad request")

    policy = RetryPolicy(
        max_attempts=5,
        base_delay=1,
    )

    wrapped = policy(fail_fatal)

    with pytest.raises(FatalError):
        wrapped()

    assert calls["count"] == 1
    assert policy.last_retry_count == 0
