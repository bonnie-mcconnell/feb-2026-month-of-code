from typing import Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LogRecord(BaseModel):
    timestamp: str
    service: str
    environment: str
    level: LogLevel
    correlation_id: str
    event: str
    latency_ms: int | None = None
    error_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: str) -> str:
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("timestamp must be ISO8601 UTC")
        return value

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(value) > 15:
            raise ValueError("metadata exceeds 15 keys")
        for k, v in value.items():
            if isinstance(v, dict):
                raise ValueError("nested metadata not allowed")
        return value

    @field_validator("latency_ms")
    @classmethod
    def validate_latency(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("latency must be >= 0")
        return value