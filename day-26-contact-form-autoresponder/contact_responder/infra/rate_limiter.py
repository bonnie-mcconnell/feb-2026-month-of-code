from collections import defaultdict
from time import time
from typing import DefaultDict

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: DefaultDict[str, list[float]] = defaultdict(list)

    def allow(self, key: str) -> bool:
        now = time()
        timestamps = self.requests[key]

        # remove expired
        self.requests[key] = [
            t for t in timestamps if now - t < self.window
        ]

        if len(self.requests[key]) >= self.max_requests:
            return False

        self.requests[key].append(now)
        return True