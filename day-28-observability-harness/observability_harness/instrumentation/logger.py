from datetime import datetime, timezone
from contracts.logging_schema import LogRecord
from typing import Any
from pydantic import ValidationError


class StructuredLogger:
    def __init__(self, service: str, environment: str):
        self.service = service
        self.environment = environment

    def log(
        self,
        event: str,
        level: str,
        correlation_id: str,
        latency_ms: int | None = None,
        error_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> LogRecord:
        metadata = metadata or {}
        record_dict = {
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "service": self.service,
            "environment": self.environment,
            "level": level,
            "correlation_id": correlation_id,
            "event": event,
            "latency_ms": latency_ms,
            "error_type": error_type,
            "metadata": metadata,
        }
        try:
            record = LogRecord(**record_dict)
        except ValidationError as e:
            raise ValueError(f"Invalid log record: {e}")
        return record