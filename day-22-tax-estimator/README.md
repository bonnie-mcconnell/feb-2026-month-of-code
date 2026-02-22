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
      vat.py
      credits.py

  services/
      estimator.py
      vat_estimator.py

  cli/
      main.py

  api/
      main.py

config/
  jurisdictions/
      nz_self_employed.json
      us_self_employed.json
      uk_self_employed.json

tests/
```

- Multi-year jurisdiction versioning currently supported for NZ, US, and UK.
- Each JSON config contains validated tax brackets, self-employment rates, and rounding rules.

### Domain Layer

- Pure computation. No I/O. No side effects.
  - Money - immutable Decimal value object
  - TaxBracket/TaxSchedule - validated bracket model
  - DeductionSet - deduction logic
  - Jurisdiction - validated policy loader
  - VAT - immutable value object that computes VAT amounts and gross-from-net conversions
  - TaxCredit/FlatCredit - abstract base for tax credit plug-ins; supports flat credits and can be extended for complex credit logic

### Service Layer

Coordinates domain objects.
- TaxEstimator - coordinates domain objects, applies deductions, computes income tax, self-employment tax, total tax, and effective rate; supports TaxCredit plug-ins
- VATService - wraps VAT domain object for service-layer usage, computing VAT on net amounts or deriving gross amounts

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
- Standard/itemized deductions are mutually exclusive.
- Business deductions separate from standard/itemized.
- All numbers are Decimal for deterministic arithmetic.
- VAT module and TaxCredit plug-ins allow extension for indirect taxes or reductions, keeping computations deterministic and Decimal-only.

## CLI Usage

### Single Estimate
```bash
python -m tax_engine.cli.main \
    --jurisdiction nz_self_employed \
    --income 120000 \
    --business-expenses 10000 \
    [--standard-deduction 5000] \
    [--itemized-deduction 7000] \
    [--year 2024]
```

### Simulate Effective Rate Curve

You can simulate multiple income levels to see how the effective tax rate changes:
```bash
python -m tax_engine.cli.main \
    --jurisdiction nz_self_employed \
    --simulate 10000 50000 10000
```

Example CSV output:
```
Income,EffectiveRate
10000,0.205000
20000,0.226000
30000,0.242333
40000,0.250500
50000,0.260400
```

- Useful for plotting effective tax rate curves.
- Automatically uses zero deductions unless overridden by standard/itemized/business.

- `--simulate START END STEP`: generates CSV output of income vs effective rate.
- `--year`: optional tax year to select config like nz_self_employed_2024.json.
- `--standard-deduction` / `--itemized-deduction`: mutually exclusive deduction inputs.

Example output:
```bash
--- Tax Estimation Result ---
Jurisdiction: NZ_SELF_EMPLOYED
Gross income: 120000.00
Total deductions: 10000.00
Taxable income: 110000.00
Income tax: 29920.00
Self-employment tax: 0.00
Total tax: 29920.00
Effective rate: 0.2493
```

- Gross income: before deductions
- Total deductions: sum of standard/itemized + business deductions
- Taxable income: income after deductions
- Income tax: computed from tax brackets
- Self-employment tax: computed if applicable
- Total tax: sum of all taxes
- Effective rate: total_tax / gross_income

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

Current coverage is ~90% of tax_engine modules (domain, services, CLI, API).
Ensures correctness for Money, brackets (and bracket properties), deductions, jurisdiction, VAT computations, TaxCredit logic, estimator logic and CLI.

## FastAPI API
Run server:
```bash
uvicorn tax_engine.api.main:app --reload
```
POST /estimate (JSON body)
```
{
  "jurisdiction": "nz_self_employed",
  "income": "120000",
  "business_expenses": "10000",
  "year": "2024"
}
```

Response Example
```json
{
  "gross_income": "120000.00",
  "taxable_income": "110000.00",
  "income_tax": "29920.00",
  "self_employment_tax": "0.00",
  "total_tax": "29920.00",
  "effective_rate": "0.2493"
}
```

- self_employment_tax is "0.00" if not applicable.
- gross_income and taxable_income use Decimal formatting for exactness.

## Extension Ideas

> Currently, the CLI and API focus on income, deductions, and self-employment tax. VAT and TaxCredit modules exist for future integration, including multi-jurisdiction VAT or credit schemes.

- Add VAT/GST module (currently implemented but can be extended per jurisdiction)
- Expand TaxCredit plug-in system (currently supports FlatCredit, extendable)
- Multi-year jurisdiction versioning (NZ, US, UK configs included in v1)
- React frontend
- Simulation curves and export