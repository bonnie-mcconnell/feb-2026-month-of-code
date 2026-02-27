# Cloud Backup

Deterministic, incremental backup engine with snapshot retention and pluggable storage backends.

Cloud Backup is a production-grade CLI tool designed for reliable filesystem backups to either local storage or Amazon S3. It emphasizes correctness, repeatability, and observability while remaining lightweight and dependency-minimal.

## Features

- Incremental, content-aware backups
- Snapshot-based retention policy
- Local filesystem storage backend
- Amazon S3 storage backend
- Parallel upload execution
- Integrity verification mode
- Structured JSON logging
- Retry with configurable backoff
- Deterministic snapshot indexing
- 90%+ automated test coverage

## Installation 

Requires Python 3.11+

Install in editable mode:
```bash
pip install -e .
```

After installation, the CLI is available as:
```bash
cloud-backup
```

## Quick Start
### 1. Create a configuration file

`config.json`
```json
{
  "source_directory": "data",
  "storage": {
    "type": "local",
    "destination": "backups"
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
```
### 2. Run a backup
```bash
cloud-backup --config config.json
```

## CLI Options
```bash
--config        Path to configuration file (required)
--dry-run       Simulate backup without writing data
--force-full    Force a full snapshot
--verify        Verify integrity of latest snapshot
--debug         Enable verbose JSON logging
--version       Show installed version
```

Examples:
```bash
cloud-backup --config config.json --dry-run
cloud-backup --config config.json --force-full
cloud-backup --config config.json --verify
```

## Storage Backends
### Local Filesystem
```json
"storage": {
  "type": "local",
  "destination": "backups"
}
```

Snapshots and index are stored in the destination directory.

### Amazon S3
```json
"storage": {
  "type": "s3",
  "bucket": "my-backup-bucket",
  "prefix": "daily/"
}
```

Requires AWS credentials configured via environment variables or standard AWS configuration mechanisms.

## How It Works
### Incremental Backups

Files are scanned and hashed. Only new or changed files are uploaded. Unchanged files are skipped.

### Snapshot Retention

Snapshots are timestamped. Retention policies enforce:
- Keep last N snapshots
- Keep snapshots newer than X days

Old snapshots are pruned deterministically.

### Index Store

An index file tracks file hashes and snapshot metadata to guarantee consistency and support incremental behavior.

### Parallel Execution

Uploads are processed concurrently for improved performance on large datasets.

### Retry Mechanism

Storage operations are retried with configurable exponential-style backoff.

### Verification Mode

`--verify` re-hashes and validates the most recent snapshot to ensure data integrity.

## Architecture

The system follows a layered, testable design:
- Domain Layer — Pure data models (snapshots, file records, retention rules)
- Engine Layer — Backup orchestration, indexing, retention enforcement
- Storage Layer — Abstract adapter interface with local and S3 implementations
- Infrastructure Layer — Configuration loading, retry logic, structured logging
- CLI Layer — Argument parsing and execution entrypoint

The design keeps business logic independent from storage implementation.

## Logging

All operational output is structured JSON, making it suitable for:
- Log aggregation systems
- Monitoring pipelines
- CI environments

Example:
```json
{"event":"backup_completed","snapshot_id":"2026-02-27T09:03:35Z","files_backed_up":1}
```

## Testing

Run full test suite with coverage:
```bash
pytest --cov=cloud_backup --cov-report=term-missing
```

Coverage: 90%+

Tests include:
- Engine integration
- CLI behavior
- Retention logic
- Retry handling
- Local and S3 adapters
- Verification workflow

## Project Structure
```
cloud_backup/
  cli/
  domain/
  engine/
  infra/
  storage/
  tests/
```

Clear separation of concerns allows easy extension of storage backends and retention strategies.

## Version
```bash
cloud-backup --version
```
Currently 0.1.0

## License

MIT 