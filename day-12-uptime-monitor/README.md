# Uptime Monitor (SQLite-backed CLI)

A minimal, production-oriented uptime monitoring tool with deterministic checks, typed results, and persistent history.

## Features

- Perform HTTP health checks
- Status classification: **UP**, **DEGRADED**, **DOWN**
- Persist results to SQLite
- Detect status transitions
- Calculate uptime statistics (DEGRADED counts as 50% uptime)
- CLI interface:
  - `run` - perform checks
  - `report <url>` - show summary
  - `history <url>` - show past checks

## Architecture

- **checker.py** – performs HTTP checks and classifies results  
- **monitor.py** – orchestrates checks, detects transitions, writes to storage  
- **storage.py** – SQLite persistence; returns typed domain models  
- **models.py** – domain entities (`CheckResult`, `Status`)  
- **cli.py** – user interface; no business logic  

This separation ensures **testability**, **clear responsibilities**, and easy swapping of persistence backend (e.g, SQLite -> Postgres).

## Status Logic

| Status       | Condition |
|--------------|-----------|
| **UP**       | HTTP < 500 and under degraded threshold |
| **DEGRADED** | HTTP < 500 but slower than configured threshold |
| **DOWN**     | HTTP >= 500 or network error |

**Uptime % calculation (Python):**
```python
uptime_pct = (up_count + 0.5 * degraded_count) / total_checks * 100

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```
## Usage

Run checks:
```bash
python -m uptime_monitor.cli run
```

Generate report:
```bash
python -m uptime_monitor.cli report https://example.com
```

Show history:
```bash
python -m uptime_monitor.cli history https://example.com
```

## Testing
```bash
pytest
```

Tests cover classification logic, transition detection, storage correctness, summary calculations, and CLI smoke tests.

## Design Philosophy

- Deterministic, synchronous logic
- No external monitoring services
- No background threads or async complexity
- Focused on core signal