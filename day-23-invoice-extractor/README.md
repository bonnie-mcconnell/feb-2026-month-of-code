# Deterministic Invoice Extractor

High-signal, deterministic PDF invoice extraction system.

## Features

- Strict financial primitives (Money, Invoice, LineItem)
- Deterministic parsing pipeline
- Vendor strategy registry
- Validation engine with explicit error codes
- Property-based tests
- CI-ready
- 100% coverage target

## Install

pip install -e .[dev]

## CLI Usage

Extract invoice:

python -m invoice_extractor.main sample.pdf

Output JSON:

python -m invoice_extractor.main sample.pdf --json

Strict validation (fail on math mismatch):

python -m invoice_extractor.main sample.pdf --json --strict

## Test

pytest --cov=invoice_extractor

## Architecture

PDF → Text Extractor → Strategy → Segmenter → Field Mapper → Line Item Parser → Domain → Validation

## Deterministic Guarantees

- No fuzzy parsing
- No heuristics
- Strict regex
- Financial math enforced
- Explicit error codes