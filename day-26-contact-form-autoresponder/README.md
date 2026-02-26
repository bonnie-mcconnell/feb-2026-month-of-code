# Contact Form Auto-Responder

A layered FastAPI service for handling contact form submissions. This service:

- Validates user input
- Detects spam using configurable heuristics
- Enforces IP-based rate limiting
- Sends autoresponses to valid, non-spam submissions

Designed for clean architecture, deterministic behavior, and full test coverage.

---

## Features

- Structured input validation (Pydantic)
- Deterministic spam scoring engine
- Config-driven thresholds (`contact_responder/config/settings.json`)
- IP-based rate limiting
- Background autoresponse dispatch
- Strict separation of layers
- Fully unit tested with 99% coverage
- Type-checked (`mypy`) and lint clean (`ruff`)

---

## Architecture
```
contact_responder/
│
├── domain/ # Pure business logic (validation, spam, message, audit)
├── services/ # Orchestration layer (ResponderService)
├── api/ # FastAPI transport layer
├── infra/ # Config loading, logging, rate limiting
├── background/ # Email dispatch side effects
├── bootstrap.py # Application composition root
└── tests/  # Unit tests for all layers (99% coverage)
```

**Design Principles**

- Domain layer contains no framework dependencies
- Deterministic spam scoring
- Configurable thresholds via `settings.json`
- Explicit dependency injection
- Background side effects isolated from core logic
- Defensive validation and throttling

---

## Spam Detection Heuristics

- Blacklisted phrases
- Suspicious phrases
- Link count threshold
- Excessive message length
- Repeated characters
- Duplicate fingerprint detection

Configured in: `contact_responder/config/settings.json`

Unit tests use a lowered threshold to ensure deterministic spam detection, production uses `settings.json` values

---

## Running Locally

```bash
pip install -r requirements.txt
uvicorn contact_responder.bootstrap:app --reload
```

Interactive API docs: http://127.0.0.1:8000/docs

## Example Requests

Valid message:
```
POST /contact
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "subject": "Hello",
  "message": "Interested in your services."
}
```

Response:
```
{
  "status": "ok",
  "message_id": "generated-id",
  "spam_score": 0,
  "is_spam": false
}
```

`message_id` is a generated UUID per submission.

Spam message (config-dependent):
```
POST /contact
{
  "name": "Spam Bot",
  "email": "spam@example.com",
  "subject": "Buy now",
  "message": "buy now buy now buy now"
}
```

Response:
```
{
  "status": "ok",
  "message_id": "generated-id",
  "spam_score": 1,
  "is_spam": true
}
```

Invalid payload (too short, bad email):

Returns 422 
Unprocessable Entity per FastAPI validation.

## Testing
```bash
pytest --cov=contact_responder --cov-report=term-missing
mypy contact_responder
ruff check .
```

Uses _config_test() for deterministic spam detection in unit tests