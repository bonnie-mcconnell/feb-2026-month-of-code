import pytest
from contracts.logging_schema import LogRecord
from pydantic import ValidationError
from typing import TypedDict, Optional, Dict, Any


class LogRecordDict(TypedDict):
    timestamp: str
    service: str
    environment: str
    level: str
    correlation_id: str
    event: str
    latency_ms: Optional[int]
    error_type: Optional[str]
    metadata: Dict[str, Any]

def test_valid_log_record():
    record = LogRecord(
        timestamp="2026-01-01T00:00:00Z",
        service="test-service",
        environment="dev",
        level="INFO",
        correlation_id="abc123",
        event="test-event",
        latency_ms=100,
        error_type=None,
        metadata={}
    )
    assert record.service == "test-service"


def test_invalid_level():
    with pytest.raises(ValidationError):
        LogRecord(
            timestamp="2026-01-01T00:00:00Z",
            service="test",
            environment="dev",
            level="INVALID",
            correlation_id="abc",
            event="x",
            latency_ms=None,
            error_type=None,
            metadata={}
        )


def test_missing_required_field():
    with pytest.raises(ValidationError):
        LogRecord(
            timestamp="2026-01-01T00:00:00Z",
            service="test",
            environment="dev",
            level="INFO",
            correlation_id="abc",
            # event missing # type: ignore
            metadata={}
        )


def base_record() -> LogRecordDict:
    return {
        "timestamp": "2026-01-01T00:00:00Z",
        "service": "svc",
        "environment": "dev",
        "level": "INFO",
        "correlation_id": "abc",
        "event": "evt",
        "latency_ms": 10,
        "error_type": None,
        "metadata": {},
    }


def test_invalid_timestamp():
    data = base_record()
    data["timestamp"] = "invalid"
    with pytest.raises(ValidationError):
        LogRecord(**data)


def test_negative_latency():
    data = base_record()
    data["latency_ms"] = -5
    with pytest.raises(ValidationError):
        LogRecord(**data)


def test_nested_metadata():
    data = base_record()
    data["metadata"] = {"nested": {"bad": "value"}}
    with pytest.raises(ValidationError):
        LogRecord(**data)


def test_metadata_too_large():
    data = base_record()
    data["metadata"] = {str(i): i for i in range(16)}
    with pytest.raises(ValidationError):
        LogRecord(**data)