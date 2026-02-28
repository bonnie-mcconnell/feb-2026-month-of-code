from functools import wraps
from typing import Callable, TypeVar, Any

from observability_harness.instrumentation.logger import emit_log
from observability_harness.contracts.logging_schema import LogLevel

T = TypeVar("T")


def retry(attempts: int = 3):
    if attempts <= 0:
        raise ValueError("attempts must be > 0")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exc: Exception | None = None

            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    emit_log(
                        service="unknown",
                        environment="dev",
                        level=LogLevel.WARNING,  # ← type-safe
                        correlation_id="retry",
                        event="retry_attempt",
                        metadata={"attempt": attempt},
                    )

            assert last_exc is not None
            raise last_exc  # safe: always assigned above

        return wrapper

    return decorator