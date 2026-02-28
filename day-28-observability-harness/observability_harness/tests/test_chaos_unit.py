import pytest
from observability_harness.chaos.injectors import (
    maybe_inject_latency,
    maybe_inject_exception,
    maybe_simulate_disk_failure,
    maybe_simulate_timeout,
)
from observability_harness.chaos.toggles import ChaosConfig


def test_latency_injected() -> None:
    called = {"slept": False}

    def sleep_fn(ms: int) -> None:
        called["slept"] = True

    def fn() -> int:
        return 1

    chaos = ChaosConfig(enabled=True, inject_latency_ms=5)
    result = maybe_inject_latency(fn, chaos=chaos, sleep_fn=sleep_fn)

    assert result == 1
    assert called["slept"]


def test_exception_injected() -> None:
    chaos = ChaosConfig(enabled=True, force_exception=True)

    def fn() -> int:
        return 1

    with pytest.raises(RuntimeError):
        maybe_inject_exception(
            fn,
            chaos=chaos,
            exception_factory=lambda: RuntimeError("boom"),
        )


def test_disk_failure() -> None:
    chaos = ChaosConfig(enabled=True, simulate_disk_failure=True)

    with pytest.raises(IOError):
        maybe_simulate_disk_failure(chaos=chaos)


def test_timeout() -> None:
    chaos = ChaosConfig(enabled=True, simulate_timeout=True)

    with pytest.raises(TimeoutError):
        maybe_simulate_timeout(chaos=chaos)


def test_latency_not_injected() -> None:
    def fn() -> int:
        return 1

    chaos = ChaosConfig(enabled=False, inject_latency_ms=5)

    result = maybe_inject_latency(fn, chaos=chaos, sleep_fn=lambda x: None)
    assert result == 1


def test_exception_not_injected() -> None:
    chaos = ChaosConfig(enabled=False, force_exception=True)

    def fn() -> int:
        return 2

    result = maybe_inject_exception(
        fn,
        chaos=chaos,
        exception_factory=lambda: RuntimeError("boom"),
    )

    assert result == 2