from typing import Dict, Literal
from pydantic import BaseModel, Field, field_validator


# ---- Central Metric Registry ----

AllowedMetricName = Literal[
    "request_count",
    "error_rate",
    "p95_latency_ms",
    "retry_count",
    "job_failures",
    "backup_duration_ms",
    "arbitrage_spread_detected",
    "spam_rejection_rate",
]


# ---- Metric Record Contract ----

class MetricRecord(BaseModel):
    name: AllowedMetricName
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float) -> float:
        if v < 0:
            raise ValueError("metric value must be >= 0")
        return v

    @field_validator("name")
    @classmethod
    def validate_name_suffix(cls, v: str) -> str:
        if v.endswith("_ms") and not (
            v.endswith("_latency_ms") or v.endswith("_duration_ms")
        ):
            raise ValueError(
                "time-based metrics must end with '_latency_ms' or '_duration_ms'"
            )
        return v

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, labels: Dict[str, str]) -> Dict[str, str]:
        if len(labels) > 10:
            raise ValueError("too many metric labels (max 10)")
        for k, val in labels.items():
            if not k.islower():
                raise ValueError("label keys must be lowercase")
            if not isinstance(val, str):
                raise ValueError("label values must be strings")
        return labels