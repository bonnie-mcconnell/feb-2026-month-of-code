from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RequestObservation:
    timestamp: int
    latency_ms: int
    success: bool


@dataclass(frozen=True)
class SLOSpec:
    service: str
    window_minutes: int
    availability: float
    p95_latency_ms: int
    error_rate: float

    def __post_init__(self):
        if self.window_minutes <= 0:
            raise ValueError("window_minutes must be > 0")
        if not (0.0 <= self.availability <= 1.0):
            raise ValueError("availability must be between 0 and 1")
        if not (0.0 <= self.error_rate <= 1.0):
            raise ValueError("error_rate must be between 0 and 1")
        if round(self.availability, 6) != round(1 - self.error_rate, 6):
            raise ValueError("availability must equal 1 - error_rate")


@dataclass(frozen=True)
class SLOResult:
    service: str
    window_start: int
    window_end: int
    total_requests: int
    availability: float
    p95_latency_ms: int
    error_rate: float
    availability_pass: bool
    latency_pass: bool
    error_rate_pass: bool
    violated: List[str]