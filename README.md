# 28 Days of Production Engineering

A focused sprint shipping scoped, production-aware systems across APIs, data, reliability, and infrastructure. One project per day, each designed to:

* solve a concrete problem
* exercise a specific engineering skill
* be completed and documented in a single day

---

## Purpose

This repository focuses on engineering judgment. Each project has:

* a defined user or purpose
* clear constraints and tradeoffs
* deliberate scope limits to avoid over-engineering

The one-day constraint enforces realistic decision-making and shipping discipline.

Across 28 projects, this repository covers:
- API design & validation
- Rate limiting & retry logic
- Background job systems
- Deterministic text processing
- Financial calculation engines
- Structured logging
- Incremental file systems
- Hash-based change detection
- External API orchestration
- Reliability patterns
- SLO evaluation
- Observability standards
- CI quality gates
- DevOps production thinking

The final projects emphasize instrumentation, structured metrics contracts, failure simulation, reliability enforcement and deployment discipline.
The progression across the month moves from isolated utilities to reliability primitives, distributed data processing, and observability enforcement. Later projects intentionally emphasize production concerns: structured logging, bounded retries, health checks, SLO evaluation, and CI quality gates.

---

## Engineering Principles Followed

Throughout the month:
- Deterministic outputs
- Minimal external dependencies
- Explicit configuration
- No hidden global state
- Structured logging
- Retry logic with bounded backoff
- Input validation
- Idempotent operations where applicable
- Test coverage emphasis (later projects ≥90%)
- Clear commit history
- Scope discipline (freeze before overbuilding)
- Explicit failure handling paths
- Clear separation of concerns
- No speculative abstractions

Overengineering was deliberately avoided.

---

## Repository Structure

Each project lives in its own folder:

```
/day-01-project-name
/day-02-project-name
...
```

Each folder typically contains:

* `README.md` - problem description, approach, tradeoffs
* `src/` - implementation
* `tests/` - lightweight tests where relevant
* `data/` - sample inputs/outputs

Projects are self-contained. No shared framework is used, keeping each project simple and clear, avoiding hidden coupling.

### Tradeoffs and Limitations

Every project README includes a section for:

* known limitations
* possible improvements with more time

---

## Tech Stack

* **Language:** Python, TypeScript
* **Storage:** CSV, SQLite, or other simple formats
* **Libraries:** minimal, standard library preferred unless external libraries are justified

---

## Architectural Progression

- Days 1–6: Core utilities and validation
- Days 7–14: APIs, middleware, and reliability primitives
- Days 15–21: External integrations and metrics modeling
- Days 22–28: Deterministic engines, backup systems, and observability enforcement

---

## Projects

| Day | Project                              | Primary Focus                              |
| --- | ------------------------------------ | ------------------------------------------ |
| 01  | Public Business Directory Aggregator | Data ingestion & normalization             |
| 02  | Broken Link Checker (CLI)            | HTTP validation & parsing                  |
| 03  | Invoice Generator (PDF)              | Deterministic document generation          |
| 04  | Cold Email Personalization Engine    | Template rendering & controlled generation |
| 05  | Data Quality Checker                 | Validation pipelines & rule engines        |
| 06  | Email Deliverability Analyzer        | Heuristic scoring & domain analysis        |
| 07  | Webhook Normalizer & Audit Log       | Event normalization & audit logging        |
| 08  | Resume ↔ Job Description Matcher     | Text similarity & scoring logic            |
| 09  | YouTube Transcript → Action Summary  | Structured text extraction                 |
| 10  | Blog → Thread Generator              | Content transformation pipeline            |
| 11  | Decision Log / Audit Trail System    | Event modeling & immutable logs            |
| 12  | Background Job Worker System         | Job queues & asynchronous processing       |
| 13  | Config-Driven Web Scraper            | Declarative scraping engine                |
| 14  | Rate Limiting & Retry Middleware     | Reliability primitives                     |
| 15  | Stock News Sentiment Tracker         | External API orchestration                 |
| 16  | Personal Finance Analyzer            | Financial modeling                         |
| 17  | Secrets Scanner (Detection Engine)   | Static analysis & security scanning        |
| 18  | Website Uptime Monitor               | Health checks & availability tracking      |
| 19  | GitHub Repo Health Checker           | Multi-endpoint API aggregation             |
| 20  | Repo Metrics Index                   | Metrics ingestion & scoring                |
| 21  | Metrics Aggregation Dashboard        | Metrics modeling & ranking logic           |
| 22  | Freelancer Tax Estimator             | Deterministic tax calculation              |
| 23  | PDF Invoice → JSON Extractor         | Structured document parsing                |
| 24  | Crypto Arbitrage Notifier            | Multi-exchange orchestration               |
| 25  | Keyword Discovery Tool               | TF-IDF & long-tail modeling                |
| 26  | Contact Form Auto-Responder API      | Secure API design & spam mitigation        |
| 27  | Automated Cloud Backup Script        | Incremental backup & retention policies    |
| 28  | Observability & Reliability Harness  | SLO enforcement & system instrumentation   |


Each project contains a detailed README outlining constraints, design decisions, tradeoffs, and future improvements.