Note: In examples, availability and error_rate SLO checks may fail due to stochastic simulated failures.


# Observability Harness

A modular Python library for logging, retry, chaos injection, and SLO evaluation.

## Features
- Structured logging with correlation IDs
- Retry decorator
- Chaos injection (latency and exceptions)
- SLO evaluation and metrics
- Examples included (crypto arbitrage integration)

## Requirements
- Python 3.11+
- Pydantic 2.12+
- pytest 9.x

## Running Tests

python -m observability_harness.ci.run_ci


## Running Manual Validation

python manual_validation.py


## Running Example

python -m observability_harness.examples.crypto_arb_integration.example


Notes:
- Example simulates stochastic failures; SLO evaluation may sometimes fail as expected.
- Logging output uses `LogLevel` enums.

Docstrings in all functions (manual_validation.py, example.py)

Optional: Add CONTRIBUTING.md / CODE_STYLE.md if planning for external use