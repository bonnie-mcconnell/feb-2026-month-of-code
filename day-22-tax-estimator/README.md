# Deterministic Tax Engine

A config-driven, multi-jurisdiction tax computation engine built with strict Decimal arithmetic and deterministic rounding.

This project models income tax systems as validated domain objects and separates tax policy (JSON configuration) from computation logic. It is designed to demonstrate correctness, reproducibility, and clean architecture in financial software.

## Why This Exists

Most tax calculators and financial examples use floating point arithmetic, which introduces non-deterministic rounding behavior and subtle inaccuracies.

This engine enforces:
- Decimal-only arithmetic
- Explicit scale and rounding policy
- Immutable Money value objects
- Strict configuration validation
- Deterministic bracket computation
- Separation of policy from computation

This is a systems-oriented implementation.

## Architecture
```
tax_engine/
  domain/
      money.py
      brackets.py
      deduction.py
      jurisdiction.py

  services/
      estimator.py

  cli/
      main.py

config/
  jurisdictions/
      nz_self_employed.json
      us_self_employed.json
      uk_self_employed.json

tests/`
```

### Domain Layer

- Pure computation. No I/O. No side effects.
  - Money - immutable Decimal value object
  - TaxBracket/TaxSchedule - validated bracket model
  - DeductionSet - deduction logic
  - Jurisdiction - validated policy loader

### Service Layer

Coordinates domain objects.
- TaxEstimator orchestrates income, deductions, tax schedule, and self-employment tax.

### CLI Layer

Thin interface. No business logic.

## Design Principles

- No floats allowed anywhere
- All configuration values parsed as Decimal
- Bracket continuity validated
- Deterministic rounding
- Immutable value objects
- Config-driven policy
- Fully testable domain

## CLI Usage
```bash
python -m tax_engine.cli.main \
    --jurisdiction nz_self_employed \
    --income 120000 \
    --business-expenses 10000
```

Example output:
```bash
--- Tax Estimation Result ---
Jurisdiction: NZ_SELF_EMPLOYED
Gross income: 120000.00
Total deductions: 10000.00
Taxable income: 110000.00
Income tax: 29920.00
Total tax: 29920.00
Effective rate: 0.2493
```

## Running Tests
```bash
pytest
```
### Type Checking
```bash
mypy tax_engine --strict
```

### Coverage
```bash
pytest --cov=tax_engine --cov-report=term-missing
```

## FastAPI API
```bash
uvicorn tax_engine.api.main:app --reload
```
POST /estimate
```
{
  "jurisdiction": "nz_self_employed",
  "income": "120000",
  "business_expenses": "10000"
}
```

## Extension Ideas

- Add VAT/GST module
- Add tax credit plug-in system
- Multi-year jurisdiction versioning
- React frontend
- Simulation curves and export