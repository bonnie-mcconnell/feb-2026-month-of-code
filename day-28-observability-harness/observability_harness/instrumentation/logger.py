from datetime import datetime, timezone
from typing import Any, Dict, Optional

from observability_harness.contracts.logging_schema import LogRecord, LogLevel
from pydantic import ValidationError


class StructuredLogger:
    def __init__(self, service: str, environment: str):
        self.service = service
        self.environment = environment

    def log(
        self,
        event: str,
        level: LogLevel,  # ← fix type
        correlation_id: str,
        latency_ms: Optional[int] = None,
        error_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LogRecord:
        metadata = metadata or {}

        # build record explicitly, no **dict
        try:
            record = LogRecord(
                timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                service=self.service,
                environment=self.environment,
                level=level,
                correlation_id=correlation_id,
                event=event,
                latency_ms=latency_ms,
                error_type=error_type,
                metadata=metadata,
            )
        except ValidationError as e:
            raise ValueError(f"Invalid log record: {e}")

        return record


# hardened global function
def emit_log(
    *,
    service: str,
    environment: str,
    level: LogLevel,
    correlation_id: str,
    event: str,
    latency_ms: Optional[int] = None,
    error_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> LogRecord:
    """
    Create and validate a structured log record.
    Fully typed, always returns a validated LogRecord.
    """
    return LogRecord(
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        service=service,
        environment=environment,
        level=level,
        correlation_id=correlation_id,
        event=event,
        latency_ms=latency_ms,
        error_type=error_type,
        metadata=metadata or {},
    )