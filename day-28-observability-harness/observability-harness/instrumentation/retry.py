from typing import Callable, TypeVar

T = TypeVar("T")


def retry(
    fn: Callable[[], T],
    *,
    retries: int,
    sleep_fn: Callable[[int], None],
) -> T:
    if retries <= 0:
        raise ValueError("retries must be > 0")

    last_exception: Exception | None = None

    for attempt in range(retries):
        try:
            return fn()
        except Exception as exc:
            last_exception = exc
            if attempt < retries - 1:
                sleep_fn(0)

    assert last_exception is not None
    raise last_exception