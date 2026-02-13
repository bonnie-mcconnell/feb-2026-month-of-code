import random


def compute_backoff(attempt: int, base_delay: float, factor: float) -> float:
    return base_delay * (factor ** (attempt - 1))


def apply_jitter(delay: float, random_fn=random.random) -> float:
    return delay * random_fn()
