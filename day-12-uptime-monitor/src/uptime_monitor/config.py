import json
from pathlib import Path
from typing import List, Optional


class Config:
    def __init__(
        self,
        urls: List[str],
        timeout: int,
        degraded_threshold_ms: Optional[int],
    ):
        self.urls = urls
        self.timeout = timeout
        self.degraded_threshold_ms = degraded_threshold_ms


def load_config(path: str) -> Config:
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path, "r") as f:
        data = json.load(f)

    urls = data.get("urls")
    if not urls or not isinstance(urls, list):
        raise ValueError("Config must contain a list of urls")

    timeout = data.get("timeout", 5)
    degraded_threshold_ms = data.get("degraded_threshold_ms")

    return Config(
        urls=urls,
        timeout=timeout,
        degraded_threshold_ms=degraded_threshold_ms,
    )
