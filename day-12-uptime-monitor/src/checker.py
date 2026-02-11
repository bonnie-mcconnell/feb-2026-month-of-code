import time
from datetime import datetime, timezone
from typing import Optional, Dict
from urllib import request, error


class HealthChecker:
    def __init__(self, timeout: int, degraded_threshold_ms: Optional[int] = None):
        self.timeout = timeout
        self.degraded_threshold_ms = degraded_threshold_ms

    def check(self, url: str) -> Dict:
        start = time.monotonic()
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            with request.urlopen(url, timeout=self.timeout) as response:
                status_code = response.getcode()

            elapsed = (time.monotonic() - start) * 1000  # ms
            status = self._classify(status_code, elapsed)

            return {
                "url": url,
                "timestamp": timestamp,
                "status": status,
                "response_time": round(elapsed, 2),
                "error": None,
            }

        except error.HTTPError as e:
            # HTTPError is still a valid HTTP response
            elapsed = (time.monotonic() - start) * 1000
            status = self._classify(e.code, elapsed)

            return {
                "url": url,
                "timestamp": timestamp,
                "status": status,
                "response_time": round(elapsed, 2),
                "error": None,
            }

        except Exception as e:
            # Network error, timeout, DNS failure, etc.
            elapsed = (time.monotonic() - start) * 1000

            return {
                "url": url,
                "timestamp": timestamp,
                "status": "DOWN",
                "response_time": round(elapsed, 2),
                "error": str(e),
            }

    def _classify(self, status_code: int, response_time_ms: float) -> str:
        if status_code >= 500:
            return "DOWN"

        status = "UP"

        if (
            self.degraded_threshold_ms is not None
            and response_time_ms > self.degraded_threshold_ms
        ):
            status = "DEGRADED"

        return status
