# Config-Driven Web Scraper

## Problem Statement

This is a deterministic, configuration-driven web scraper designed to extract structured data
from web pages in a reproducible and testable way. It is not a generic crawling tool, but a 
focused backend engine suitable for internal pipelines, lightweight ETL jobs, or research scrapers.

## Design Philosophy

- **Separation of Concerns:**  
  Config, fetching, extraction, validation, and CLI are fully decoupled.

- **Declarative Configuration:**  
  Extraction rules (CSS selectors, required/optional fields) are loaded from JSON configs.
  No hardcoded selectors.

- **Schema Validation:**  
  All outputs are validated against a structured JSON contract.
  Includes snapshot testing and edge-case handling.

- **Resilience & Partial Failure Handling:**  
  Engine classifies extractions as SUCCESS, PARTIAL, or FAILED.
  Required validation failures and fetch errors are collected in the errors field.
  Optional field issues degrade status to PARTIAL but are not treated as hard errors.

- **Defensive Programming:**  
  Handles missing selectors, empty fields, unexpected HTML, and fetch errors gracefully.

## Configuration Example

```json
{
  "name": "example_blog",
  "targets": [
    {
      "url": "https://example.com/article1",
      "fields": {
        "title": {"selector": "h1", "required": true, "non_empty": true},
        "author": {"selector": ".author", "required": false},
        "date": {"selector": ".published", "required": false},
        "content": {"selector": ".article-body", "required": true}
      }
    }
  ]
}
```
## Usage
### Run scraper
```bash
python -m src.cli run configs/example.json

# Run scraper with JSON output file
python -m src.cli run configs/example.json --output examples/sample_output.json
```
### Output Format
```json
{
  "source": "example_blog",
  "results": [
    {
      "url": "https://example.com/article1",
      "status": "SUCCESS",
      "data": {
        "title": "Example Title",
        "content": "Article content here..."
      },
      "errors": []
    }
  ]
}
```

- status: "SUCCESS" | "PARTIAL" | "FAILED"
- errors: list of string messages explaining missing fields or fetch issues.

### Status Semantics

- SUCCESS: All required fields extracted and valid.
- PARTIAL: Required fields valid, but optional fields missing or empty.
- FAILED: One or more required fields missing or invalid, or fetch failure.

## Testing

Run the full test suite:

pytest

Includes:
- Unit tests per module
- Contract snapshot tests
- JSON schema enforcement
- Partial failure handling
- Performance guardrail


## Limitations
- No JavaScript rendering or headless browser support.
- No crawling beyond listed targets.
- Designed for small-to-medium batch scraping jobs.

## Why Config-Driven is Powerful
- Easy to maintain extraction rules without touching code.
- Supports multiple targets and multiple fields per target.
- Partial failures are explicit, enabling safe ingestion downstream.

## Optional Extensions/Next Steps
- Rate limiting between requests (configurable)
- Metrics summary (count of SUCCESS / PARTIAL / FAILED)
- Selector fallback support
- Basic pagination handling via config

## Architecture Diagram (ASCII)

```bash
configs/ ---> config_loader ---> engine ---> fetcher ---> extractor ---> validator ---> CLI / JSON output
```