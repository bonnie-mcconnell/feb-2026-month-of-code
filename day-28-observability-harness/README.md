# Observability Harness

Framework-agnostic Python library for deterministic observability and reliability.

#### Key Features:
- Structured logs & correlation IDs
- Deterministic SLO evaluation (availability = 1 - error_rate)
- CI enforcement: test coverage ≥ 90%, schema validation, optional Docker build
- Opt-in chaos & retry utilities for resilience testing (correlation, retry, timing helpers exposed)
- Examples: crypto arbitrage engine integration

#### Guarantees:
- Logs adhere to schema
- Metrics validated & CI-blocking on violation
- Deterministic SLO math
- Fail-fast CI enforcement

#### Quick Start:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m observability_harness.ci.run_ci
python manual_validation.py
python -m observability_harness.examples.crypto_arb_integration.example
```

A framework-agnostic Python library that enforces structured telemetry, validates observability contracts, evaluates deterministic SLO compliance, and enables controlled failure injection. It ensures production discipline across services without dashboards or visualization tooling.

This project focuses on enforcing observability standards or reliability contracts. It avoids:
- Lack of structured logging across services
- No deterministic SLO evaluation
- No automated chaos or resilience testing
- No CI enforcement of observability contracts

This harness enables measurable availability, fail-fast CI validation, and reproducible reliability testing.

## Architecture Overview

#### Service Layer
```
Service
  ├─ instrumentation/
  │     ├─ StructuredLogger
  │     ├─ Correlation ID propagation
  │     └─ Retry & timing helpers
  │
  ├─ chaos/
  │     ├─ Latency injection
  │     └─ Exception injection
  │
  └─ slo/
        └─ Deterministic rolling-window SLO evaluation (availability = 1 - error_rate enforced)
```

#### CI Layer
```
CI
  ├─ Coverage gate (>= 90%)
  ├─ Schema validator (logs & metrics)
  ├─ Metric contract validator
  └─ Optional Docker build verification (manual or automated)
```

## Design Philosophy

- Determinism over realism - SLOs are explicitly evaluated using rolling windows.
- Enforcement over dashboards - Validation is programmatic, not visual.
- Explicit injection over global state - Chaos is opt-in per function.
- Contracts over convention - Logs and metrics follow strict schema.
- Fail-fast CI over manual review - Violations block CI.
- Purity over framework coupling - Independent of any web framework or orchestrator.

## Module Breakdown

| Module             | Description                                                                                         |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| `contracts/`       | Canonical log schema, metric names, and SLO spec validation                                         |
| `instrumentation/` | Structured logging, correlation IDs, retry observation, timing helpers                              |
| `slo/`             | Deterministic rolling-window SLO evaluation                                                         |
| `chaos/`           | Controlled latency and exception injection for resilience testing (opt-in)                          |
| `ci/`              | Automated enforcement of test coverage, schema validation, metrics contracts, optional Docker build |
| `examples/`        | Integration scenarios demonstrating harness usage (e.g., crypto arbitrage)                          |


## Enforcement Guarantees

- Logs adhere strictly to schema.
- Invalid metrics fail CI.
- Test coverage ≥ 90%.
- SLO evaluation is deterministic.
- Docker build verification possible via explicit check.
- Chaos injection is opt-in and only used in manual validation and integration examples.
- Utilities for correlation, retry, and timing are exposed as service instrumentation helpers.

## Failure Modes Considered

- Zero traffic window = SLO failure
- No hidden global state for logging or chaos
- No probabilistic chaos outside explicit injection
- Availability and error_rate relationship enforced (availability = 1 - error_rate)
- No hidden percentile libraries or non-deterministic evaluation

## Tradeoffs & Non-Goals

- Does not provide dashboards, tracing, or message brokers
- Does not replace Prometheus, Grafana, or other production infrastructure
- Does not include Kubernetes manifests or authentication layers
- Scope discipline preserves clarity, reliability, and deterministic behavior

## Integration With other Projects

The harness can wrap API handlers, services, or scripts to:
- Enforce structured telemetry (logs, metadata, correlation IDs)
- Inject latency or exceptions during resilience tests
- Evaluate SLO compliance during CI simulations

Example: Crypto arbitrage engine logs requests, retries transient failures, injects controlled latency, and reports deterministic SLO outcomes.

## Scaling Considerations (10x Scale)

- Replace in-memory aggregation with Prometheus or streaming windows
- Centralize log ingestion
- Enable distributed tracing
- Route alerts programmatically
- The harness models governance logic, not infrastructure

## Kubernetes Integration Notes

- Health/readiness probes integrate with harness metrics
- Chaos injection disabled in production
- CI gates integrated into build pipelines
- SLO evaluation may run as a periodic job
- No deep Kubernetes manifests included

## How To Run
### Setup
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Run Tests (CI)
```bash
# Docker verification can be run manually if Docker is installed
python -m observability_harness.ci.run_ci
```

### Run Manual Validation
```bash
python manual_validation.py
```

### Run Example Integration
```bash
python -m observability_harness.examples.crypto_arb_integration.example
```

Notes:
- Example simulates stochastic failures; SLO evaluation may occasionally fail.
- Logging output uses LogLevel enums.
- Docker verification can be run manually if desired.

## CI Guarantees

- Enforces coverage ≥ 90%
- Validates log and metric schemas
- Optional Docker build verification (runs only if Docker is installed)
- Blocks merges for any violations
- Enforcement is deterministic and automated; no manual review required
- Chaos injection is opt-in for resilience testing
- Correlation, retry, and timing utilities exposed for service instrumentation