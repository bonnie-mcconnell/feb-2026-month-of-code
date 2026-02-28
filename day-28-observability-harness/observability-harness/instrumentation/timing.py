from typing import Callable, TypeVar
from time import perf_counter

T = TypeVar("T")


def timed(fn: Callable[..., T]) -> Callable[..., tuple[T, int]]:
    """Returns (result, elapsed_ms)"""
    def wrapper(*args, **kwargs) -> tuple[T, int]:
        start = perf_counter()
        result = fn(*args, **kwargs)
        end = perf_counter()
        elapsed_ms = int((end - start) * 1000)
        return result, elapsed_ms
    return wrapper