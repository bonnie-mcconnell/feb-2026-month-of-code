from typing import Callable, TypeVar
from .toggles import ChaosConfig

T = TypeVar("T")


def maybe_inject_latency(
    fn: Callable[[], T],
    *,
    chaos: ChaosConfig,
    sleep_fn: Callable[[int], None],
) -> T:
    if not chaos.enabled or chaos.inject_latency_ms is None:
        return fn()

    sleep_fn(chaos.inject_latency_ms)
    return fn()


def maybe_inject_exception(
    fn: Callable[[], T],
    *,
    chaos: ChaosConfig,
    exception_factory: Callable[[], Exception],
) -> T:
    if chaos.enabled and chaos.force_exception:
        raise exception_factory()

    return fn()


def maybe_simulate_disk_failure(
    *,
    chaos: ChaosConfig,
) -> None:
    if chaos.enabled and chaos.simulate_disk_failure:
        raise IOError("Simulated disk failure")


def maybe_simulate_timeout(
    *,
    chaos: ChaosConfig,
) -> None:
    if chaos.enabled and chaos.simulate_timeout:
        raise TimeoutError("Simulated timeout")