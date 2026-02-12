# Config-Driven Web Scraper

A deterministic, configuration-driven data extraction engine for structured web content.

This tool separates extraction rules from scraping logic, enabling reusable, declarative scraping workflows suitable for ingestion pipelines, monitoring jobs, and lightweight ETL tasks.
It is designed as a reusable backend component, not a one-off script.

---

## Problem Statement

Many web scrapers are tightly coupled scripts:

- Selectors are hardcoded
- Validation is implicit
- Errors crash execution
- Partial failures are not classified
- Output is inconsistent

This project addresses those issues by:

- Moving extraction rules into configuration
- Enforcing explicit validation
- Classifying results deterministically
- Separating HTTP, parsing, validation, and orchestration layers

---

## Design Philosophy

### Declarative Configuration

Extraction rules are defined in JSON:

```json
{
  "name": "example_blog",
  "targets": [
    {
      "url": "https://example.com/article",
      "fields": {
        "title": {
          "selector": "h1",
          "required": true,
          "non_empty": true
        }
      }
    }
  ]
}
```
The engine interprets this configuration at runtime.

No selectors are hardcoded in application logic.

### Clean Architecture

The system is intentionally layered:
- config_loader — validates configuration structure
- fetcher — handles HTTP transport and error classification
- extractor — applies CSS selectors and normalizes text
- validator — enforces required/non-empty rules
- engine — orchestrates the pipeline
- cli — user interface boundary

Each module has a single responsibility.

### Deterministic Result Classification

Each target URL results in:
- SUCCESS
- PARTIAL
- FAILED

Failures do not crash the run.
Each target is isolated.

---

## Usage

Run the scraper:
```bash
python -m src.cli run configs/example.json
```

Write output to file:
```bash
python -m src.cli run configs/example.json --output results.json
```

Exit codes:
- 0 — no failures
- 1 — at least one target failed
- 2 — configuration error

## Output Format
```json
{
  "source": "example_blog",
  "results": [
    {
      "url": "...",
      "status": "SUCCESS",
      "data": { ... },
      "errors": []
    }
  ]
}
```

---

## Limitations

- No JavaScript rendering
- No crawling or discovery
- No pagination
- No retry strategy
- No attribute or list extraction
- No schema type coercion

This tool focuses on deterministic, config-driven extraction only.

---

## Extension Ideas

- Rate limiting between requests
- Selector fallback support
- Pagination via config
- Structured logging
- Basic metrics summary

