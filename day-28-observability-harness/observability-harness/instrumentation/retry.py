from typing import Callable, TypeVar
from time import sleep

T = TypeVar("T")


def retry(fn: Callable[..., T], retries: int, sleep_fn: Callable[[int], None] = sleep) -> T:
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            if attempt < retries:
                sleep_fn(0)  # Use 0 in prod harness for deterministic tests
            else:
                raise
    if last_exc:
        raise last_exc