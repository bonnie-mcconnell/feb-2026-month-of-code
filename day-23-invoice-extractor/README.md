# Deterministic Invoice Extractor

A strictly deterministic PDF invoice extraction system built with explicit domain modeling, validation guarantees, and test-driven design.

This project focuses on correctness, traceability, and predictable behavior rather than heuristic guessing or fuzzy parsing.

## Why This Exists

An invoice extraction system that relies on heuristics, fuzzy matching, or ML pipelines introduces non-deterministic behavior and hidden failure modes. This project demonstrates an alternative:
- Explicit domain modeling
- Deterministic parsing rules
- Strict financial validation
- Full test coverage of business logic
- Clear architectural boundaries

The goal is correctness over convenience.

## Core Capabilities

- Deterministic PDF → structured invoice extraction
- Strong financial primitives (Money, Invoice, LineItem)
- Vendor-specific parsing strategies via registry pattern
- Explicit validation layer with structured error types
- JSON contract output
- CLI interface
- Real PDF integration test
- Property-based testing for monetary correctness

## Example CLI Usage

Extract invoice:
```bash
python -m invoice_extractor.main sample.pdf
```

Output structured JSON:
```bash
python -m invoice_extractor.main sample.pdf --json

python -m invoice_extractor.main invoice_extractor/tests/fixtures/sample_invoice_1.pdf --json
```

Strict validation (fail on subtotal/total mismatch):
```bash
python -m invoice_extractor.main sample.pdf --json --strict
```

## Architecture
```
PDF
  ↓
Text Extractor
  ↓
Strategy Resolver (Vendor Registry)
  ↓
Segmenter
  ↓
Field Mapper
  ↓
Line Item Parser
  ↓
Domain Model (Invoice / Money / LineItem)
  ↓
Validation Engine
  ↓
JSON Contract Output
```

## Design Principles

- No fuzzy matching
- No ML
- No hidden fallbacks
- Deterministic ISO date parsing
- Explicit currency enforcement
- Financial math consistency checks
- Structured parse errors

## Domain Modeling

Financial values use a dedicated Money value object:
- Decimal-backed
- Currency-aware
- Immutable
- Arithmetic-safe

Invoice structure is modeled explicitly via dataclasses:
- Invoice
- Vendor
- Customer
- LineItem

No dictionaries are passed through the system internally.

## Testing Strategy

54 tests
95% total coverage

Includes:
- Unit tests (domain + parsing layers)
- Property-based tests (monetary arithmetic invariants)
- Real PDF extraction test
- CLI invocation tests
- JSON snapshot contract test
- Validation failure tests
- Strategy registry failure tests

Run:
```bash
pytest --cov=invoice_extractor --cov-report=term-missing
```

## Deterministic Guarantees

- Regex-based field extraction
- Fixed ISO date parsing
- Strict numeric parsing
- Explicit parse failures (no silent fallbacks)
- Validation layer enforces:
  - subtotal consistency
  - tax correctness
  - total correctness
  - presence of line items

If parsing fails, it fails loudly.

## Current Scope

This project intentionally supports:
- Structured invoices following known layouts
- Vendor-specific strategies
- Deterministic formats

It does not include:
- OCR
- Machine learning
- Layout inference
- Fuzzy vendor detection

Those are separate architectural concerns.

## Installation
```bash
pip install -e .[dev]
```

This repository serves as a reference implementation of deterministic document extraction with strict domain modeling.

