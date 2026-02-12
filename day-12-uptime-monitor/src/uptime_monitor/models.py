from dataclasses import dataclass
from typing import Optional, Literal

Status = Literal["UP", "DOWN", "DEGRADED"]

@dataclass
class CheckResult:
    url: str
    timestamp: str  # ISO 8601 UTC
    status: Status
    response_time: Optional[float]
    error: Optional[str]
