from dataclasses import dataclass


@dataclass(frozen=True)
class ChaosConfig:
    enabled: bool = False
    inject_latency_ms: int | None = None
    force_exception: bool = False
    simulate_disk_failure: bool = False
    simulate_timeout: bool = False