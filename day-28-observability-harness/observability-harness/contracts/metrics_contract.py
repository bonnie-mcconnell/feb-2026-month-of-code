ALLOWED_METRICS = {
    "request_count",
    "error_rate",
    "p95_latency_ms",
    "retry_count",
    "job_failures",
    "backup_duration_ms",
    "arbitrage_spread_detected",
    "spam_rejection_rate",
}


def validate_metric_name(name: str) -> None:
    if name not in ALLOWED_METRICS:
        raise ValueError(f"metric '{name}' not in contract")

    if name.endswith("_ms") and not name.endswith("_latency_ms") and not name.endswith("_duration_ms"):
        raise ValueError("time-based metrics must be latency_ms or duration_ms")
    

# NEW

from pydantic import BaseModel, Field, field_validator
from typing import Dict


class MetricRecord(BaseModel):
    name: str
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.islower():
            raise ValueError("metric name must be lowercase")
        if " " in v:
            raise ValueError("metric name must not contain spaces")
        return v