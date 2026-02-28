from math import ceil
from typing import List
from .types import RequestObservation, SLOSpec, SLOResult
from .window import filter_window


def _calculate_p95(latencies: List[int]) -> int:
    if not latencies:
        return 0
    sorted_vals = sorted(latencies)
    n = len(sorted_vals)
    index = ceil(0.95 * n) - 1
    return sorted_vals[index]


def evaluate_slo(
    observations: List[RequestObservation],
    spec: SLOSpec,
    *,
    current_time: int,
) -> SLOResult:

    window_end = current_time
    window_start = current_time - (spec.window_minutes * 60)

    windowed = filter_window(
        observations,
        window_start=window_start,
        window_end=window_end,
    )

    total = len(windowed)

    if total == 0:
        return SLOResult(
            service=spec.service,
            window_start=window_start,
            window_end=window_end,
            total_requests=0,
            availability=0.0,
            p95_latency_ms=0,
            error_rate=0.0,
            availability_pass=False,
            latency_pass=False,
            error_rate_pass=False,
            violated=["no_traffic"],
        )

    successes = sum(1 for o in windowed if o.success)
    failures = total - successes

    availability = round(successes / total, 6)
    error_rate = round(failures / total, 6)

    p95_latency = _calculate_p95([o.latency_ms for o in windowed])

    availability_pass = availability >= spec.availability
    latency_pass = p95_latency <= spec.p95_latency_ms
    error_rate_pass = error_rate <= spec.error_rate

    violated = []
    if not availability_pass:
        violated.append("availability")
    if not latency_pass:
        violated.append("latency")
    if not error_rate_pass:
        violated.append("error_rate")

    return SLOResult(
        service=spec.service,
        window_start=window_start,
        window_end=window_end,
        total_requests=total,
        availability=availability,
        p95_latency_ms=p95_latency,
        error_rate=error_rate,
        availability_pass=availability_pass,
        latency_pass=latency_pass,
        error_rate_pass=error_rate_pass,
        violated=violated,
    )