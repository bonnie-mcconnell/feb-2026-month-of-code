# Deterministic Finance Analyzer

Rule-Based Financial Analytics Engine with API + Persistence

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
- **API**: 
  - FastAPI application
  - Pydantic API response models
- **Persistence Layer**:
  - SQLite database (finance.db)
  - SQLAlchemy ORM models
  - Repository abstraction layer
  - Database initialization script (init_db.py)


No business logic lives in the CLI.

All financial computations use `Decimal` to avoid floating-point precision errors.

The project uses SQLite for persistence.
Default location is at root folder:
finance.db

If the file does not exist, run:
```bash
python -m src.init_db
```
Re-ingesting the same file will create duplicate records. The system does not enforce idempotency.
This is expected behavior in v0.1.0.



Database Schema
```
transactions
- id
- date
- description
- amount
- category (nullable)
- is_expense
- created_at

reports
- year
- month
- total_income
- total_expense
- created_at

anomalies
- type
- message
- year
- month
- amount
- category
- created_at
```
---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## System Modes

### Execution Modes

The system can run in three modes:
- CLI (stateless)
- REST API (FastAPI)
- Persistent mode (SQLite-backed ingestion)


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


## REST API

Run:

```bash
uvicorn src.api:app --reload
```

Interactive docs:
```bash
http://127.0.0.1:8000/docs
```

Example API Call
```bash
curl -X POST \
  http://127.0.0.1:8000/analyze \
  -F "file=@data/sample_transactions.csv"
```

Example API Response

POST /analyze
```json
{
  "report": {
    "monthly_summaries": [
      {
        "year": 2024,
        "month": 2,
        "total_income": "2500.00",
        "total_expense": "40.39",
        "spending_by_category": {
          "Food & Drink": "5.40",
          "Shopping": "34.99"
        }
      }
    ]
  },
  "anomalies": [
    {
      "type": "large_transaction",
      "message": "Large expense detected: 1200.00",
      "year": 2024,
      "month": 3,
      "amount": "1200.00",
      "category": null
    }
  ]
}
```

## Docker Section
```bash
docker compose up --build
```
This mounts ./data to persist the SQLite database outside the container.

Build:
```bash
docker build -t finance-analyzer .
```
Run:
```bash
docker run -p 8000:8000 finance-analyzer
```

The API will be available at:
http://localhost:8000/docs

- Spins up API
- SQLite volume mounted
- Production-ready container structure


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

- PostgreSQL production backend
- Authentication & multi-user isolation
- Scheduled recurring ingestion
- Web dashboard
- ML-based category suggestion engine
- Real-time anomaly alerts
- Multi-currency support
- Detailed API response documentation
