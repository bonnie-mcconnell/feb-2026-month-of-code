from pydantic import BaseModel, field_validator


class SLOSpec(BaseModel):
    service: str
    window_minutes: int
    availability: float
    p95_latency_ms: int
    error_rate: float

    @field_validator("window_minutes")
    @classmethod
    def validate_window(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("window_minutes must be > 0")
        return value

    @field_validator("availability")
    @classmethod
    def validate_availability(cls, value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("availability must be between 0 and 1")
        return value

    @field_validator("error_rate")
    @classmethod
    def validate_error_rate(cls, value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("error_rate must be between 0 and 1")
        return value

    @field_validator("p95_latency_ms")
    @classmethod
    def validate_latency(cls, value: int) -> int:
        if value < 0:
            raise ValueError("latency must be >= 0")
        return value

    @field_validator("error_rate")
    @classmethod
    def validate_consistency(cls, value: float, info):
        availability = info.data.get("availability")
        if availability is not None:
            if round(1 - value, 6) != round(availability, 6):
                raise ValueError("availability must equal 1 - error_rate")
        return value