from decimal import Decimal
from typing import Callable, Iterable, Type
from time import sleep


class RetryError(Exception):
    """Raised when retry attempts are exhausted."""


def retry(
    func: Callable[[], object],
    *,
    max_attempts: int,
    base_delay: Decimal,
    backoff_multiplier: Decimal,
    retry_on: Iterable[Type[Exception]],
    sleep_func: Callable[[float], None] | None = None,
) -> object:
    if max_attempts <= 0:
        raise ValueError("max_attempts must be positive")

    if base_delay <= Decimal("0"):
        raise ValueError("base_delay must be positive")

    if backoff_multiplier < Decimal("1"):
        raise ValueError("backoff_multiplier must be >= 1")

    sleep_func = sleep_func or sleep

    attempt = 0
    delay = base_delay

    while True:
        try:
            return func()
        except Exception as exc:
            attempt += 1

            if not isinstance(exc, tuple(retry_on)):
                raise

            if attempt >= max_attempts:
                raise RetryError("Retry attempts exhausted") from exc

            sleep_func(float(delay))
            delay *= backoff_multiplier