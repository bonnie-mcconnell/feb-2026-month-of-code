from dataclasses import dataclass
import yaml


@dataclass(frozen=True)
class SLOSpec:
    service: str
    window_minutes: int
    availability: float
    p95_latency_ms: int
    error_rate: float


def load_slo_yaml(path: str) -> SLOSpec:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    spec = SLOSpec(
        service=raw["service"],
        window_minutes=raw["window_minutes"],
        availability=raw["slo"]["availability"],
        p95_latency_ms=raw["slo"]["p95_latency_ms"],
        error_rate=raw["slo"]["error_rate"],
    )

    validate_slo_spec(spec)
    return spec


def validate_slo_spec(spec: SLOSpec) -> None:
    if not 0 <= spec.availability <= 1:
        raise ValueError("availability must be between 0 and 1")

    if not 0 <= spec.error_rate <= 1:
        raise ValueError("error_rate must be between 0 and 1")

    if spec.window_minutes <= 0:
        raise ValueError("window_minutes must be > 0")

    if round(1 - spec.error_rate, 6) != round(spec.availability, 6):
        raise ValueError("availability must equal 1 - error_rate")