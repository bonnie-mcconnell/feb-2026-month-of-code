Automated Cloud Backup

A production-grade backup engine supporting:

Local filesystem storage

Amazon S3 storage

Snapshot-based retention

Incremental backups

Parallel uploads

Integrity verification

Structured JSON logging

Retry with backoff

90%+ test coverage

Installation
pip install -e .
Configuration
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
Usage

Run backup:

backup --config config.json

Dry run:

backup --config config.json --dry-run

Force full:

backup --config config.json --force-full

Verify integrity:

backup --config config.json --verify
Architecture

Domain layer (pure models)

Engine layer (business logic)

Infra layer (config, retry, logging)

Storage abstraction (local + S3)

Snapshot retention engine

Parallel upload execution

Testing
pytest --cov=cloud_backup --cov-report=term-missing