# Deterministic Finance Analyzer

A stateless, rule-based personal finance analytics engine written in Python.

This project ingests transaction CSV files, categorizes spending using configurable rules, generates monthly financial reports, and detects anomalies such as large transactions and spending spikes.

The system is designed to be deterministic, testable, and production-ready in structure.

---

## Features

- CSV transaction ingestion
- Rule-based categorization (config-driven)
- Monthly income and expense aggregation
- Category spending breakdown
- Top spending category detection
- Large transaction detection
- Monthly spending spike detection
- Stateless CLI interface
- 100% deterministic financial calculations (Decimal-based)
- Full unit test coverage of core engine

---

## Architecture

The system is intentionally layered:
```text
CLI → Engine → Services → Domain Models
```

- **CLI**: Thin orchestration layer (argparse)
- **Engine**: Coordinates analysis flow
- **Services**:
  - Categorization
  - Aggregation
  - Anomaly detection
- **Domain Models**:
  - Transaction
  - MonthlySummary
  - Report
  - Anomaly

No business logic lives in the CLI.

All financial computations use `Decimal` to avoid floating-point precision errors.

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Usage
### Analyze full dataset
```bash
python -m src.cli analyze data/sample_transactions.csv
```

### Generate report only
```bash
python -m src.cli report data/sample_transactions.csv
```

### Detect anomalies only
```bash
python -m src.cli anomalies data/sample_transactions.csv
```

## Configuration

Categorization rules are defined in config/categories.json

Rules are evaluated deterministically in order.

## Testing
```bash
pytest
```

The core engine is fully unit tested.

## Design Principles

- Deterministic outputs
- No floating-point math for currency
- Clear separation of concerns
- Stateless CLI
- Test-driven core logic
- Minimal dependencies
- Extensible service architecture

## Future Improvements

- Persistence layer (SQLite/PostgreSQL)
- Visualization dashboard
- REST API wrapper
- ML-based categorization module
- Multi-currency support