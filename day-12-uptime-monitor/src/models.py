from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckResult:
    url: str
    timestamp: str
    status: str
    response_time: Optional[float]
    error: Optional[str]
