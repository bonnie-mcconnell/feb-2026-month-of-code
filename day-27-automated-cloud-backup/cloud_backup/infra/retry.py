import time
from typing import Callable, Type, Tuple, Any


class RetryExceededError(Exception):
    pass


def retry(
    fn: Callable[[], Any],
    *,
    max_attempts: int,
    backoff_seconds: float,
    retry_on: Tuple[Type[BaseException], ...],
) -> Any:
    """
    Execute fn with exponential backoff.
    Does not log. Raises RetryExceededError if exhausted.
    """

    if max_attempts <= 0:
        raise ValueError("max_attempts must be >= 1")

    attempt = 0
    last_exc: BaseException | None = None

    while attempt < max_attempts:
        try:
            return fn()
        except retry_on as exc:
            last_exc = exc
            attempt += 1

            if attempt >= max_attempts:
                break

            sleep_time = backoff_seconds * (2 ** (attempt - 1))
            time.sleep(sleep_time)

        except Exception:
            # Non-retryable error — fail immediately
            raise

    raise RetryExceededError(
        f"Retry attempts exhausted: {max_attempts}"
    ) from last_exc