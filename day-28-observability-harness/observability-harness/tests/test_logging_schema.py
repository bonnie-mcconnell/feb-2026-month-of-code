import pytest
from contracts.logging_schema import LogRecord
from pydantic import ValidationError


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
            event="x",
            metadata={}
        )