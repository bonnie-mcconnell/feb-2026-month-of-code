import json
import os
from dataclasses import dataclass
from typing import Optional

from cloud_backup.domain.retention import RetentionPolicy


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int
    backoff_seconds: float


@dataclass(frozen=True)
class StorageConfig:
    type: str
    destination: Optional[str] = None  # local only
    bucket: Optional[str] = None       # s3 only
    prefix: Optional[str] = None       # s3 optional

@dataclass(frozen=True)
class AppConfig:
    source_directory: str
    storage: StorageConfig
    retention: RetentionPolicy
    retry: RetryConfig


def load_config(path: str) -> AppConfig:
    if not os.path.exists(path):
        raise ConfigError(f"Config file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        raise ConfigError(f"Invalid JSON config: {e}") from e

    try:
        source_directory = raw["source_directory"]

        storage_raw = raw["storage"]
        storage_type = storage_raw["type"]

        if storage_type == "local":
            storage = StorageConfig(
                type="local",
                destination=storage_raw["destination"],
            )
        elif storage_type == "s3":
            storage = StorageConfig(
                type="s3",
                bucket=storage_raw["bucket"],
                prefix=storage_raw.get("prefix", ""),
            )
        else:
            raise ConfigError(f"Unsupported storage type: {storage_type}")
        

        if storage_type == "local" and not storage.destination:
            raise ConfigError("local storage requires destination")

        if storage_type == "s3" and not storage.bucket:
            raise ConfigError("s3 storage requires bucket")
        
        if storage_type == "local" and storage.bucket is not None:
            raise ConfigError("local storage must not define bucket")

        retention_raw = raw["retention"]
        retention = RetentionPolicy(
            retain_last=retention_raw["retain_last"],
            retain_days=retention_raw["retain_days"],
        )
        retention.validate()

        retry_raw = raw["retry"]
        retry = RetryConfig(
            max_attempts=retry_raw["max_attempts"],
            backoff_seconds=retry_raw["backoff_seconds"],
        )

    except KeyError as e:
        raise ConfigError(f"Missing required config field: {e}") from e

    if retry.max_attempts < 1:
        raise ConfigError("retry.max_attempts must be >= 1")

    return AppConfig(
        source_directory=source_directory,
        storage=storage,
        retention=retention,
        retry=retry,
    )


"""
EXAMPLE CONFIG

{
  "source_directory": "./data",
  "storage": {
    "type": "local",
    "destination": "./backups"
  },
  "retention": {
    "retain_last": 5,
    "retain_days": 14
  },
  "retry": {
    "max_attempts": 3,
    "backoff_seconds": 2
  }
}
"""

