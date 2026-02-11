# Decision Log / Audit Trail System

A focused, append-only system for recording and reviewing decisions made by humans or automated processes.

Built for engineering environments where history, traceability, and accountability matter.

## What This System Does

- Records immutable decisions with context, rationale, tradeoffs, and tags
- Persists decisions in an append-only JSON log
- Supports append-only outcome tracking (no mutation)
- Provides filtering and statistics via CLI
- Supports JSON output for automation and dashboards
- Maintains a versioned schema for forward compatibility

This is an audit trail, not CRUD.

## Core Principles
### 1. Immutable Decisions

- Decision is a frozen dataclass
- ID and timestamp are generated automatically
- Includes a version field for schema evolution
- No in-place updates allowed

### 2. Append-Only Storage

- decisions.json is rewritten on append
- No deletes
- No edits
- Full historical integrity

### 3. Append-Only Outcomes

Outcomes are stored separately in outcomes.json.
- Each outcome references a decision_id
- Multiple outcomes allowed
- No mutation of original decisions
- Preserves temporal history

### 4. Separation of Concerns

- log.py → recording decisions
- outcomes.py → recording outcomes
- query.py → read-only filtering
- storage.py → persistence
- cli.py → thin orchestration layer

No logic buried in the CLI.

## Project Structure
```text
day-11-decision-log/
├── README.md
├── src/
│   ├── models.py          # Immutable decision model (versioned)
│   ├── storage.py         # Append-only JSON persistence
│   ├── log.py             # Decision recording API
│   ├── outcomes.py        # Append-only outcome tracking
│   ├── query.py           # Read-only decision filters
│   ├── metrics.py         # Aggregation helpers (counts, breakdowns)
│   ├── export.py          # CSV export utilities
│   └── cli.py             # CLI orchestration layer
├── tests/
│   ├── test_decisions.py
│   ├── test_outcomes.py
│   ├── test_cli_integration.py
│   └── test_input.json    # Fixture for CLI input testing
├── data/
│   ├── decisions.json
│   └── inputs.json        # Example JSON input for CLI usage
```
## CLI Overview

Global option:
```bash
--storage-path PATH
```

Optional for outcome commands:
```bash
--outcome-storage-path PATH
```

## Commands
### Add a Decision
PowerShell-safe inline JSON
```bash
python -m src.cli add `
  --actor "alice" `
  --title "Choose database" `
  --description "Use SQLite for prototype" `
  --context "Early stage" `
  --inputs '{""options"": [""SQLite"", ""Postgres""]}'
```

Using file input (recommended)
```bash
python -m src.cli add `
  --actor "alice" `
  --title "Choose database" `
  --description "Use SQLite for prototype" `
  --context "Early stage" `
  --inputs-file data/inputs.json
```

You can also use shorthand:
```bash
--inputs @data/inputs.json
```

### List Decisions
```bash
python -m src.cli list
```

Filter by actor:
```bash
python -m src.cli list --actor alice
```

Filter by date range:
```bash
python -m src.cli list `
  --start 2026-02-01T00:00:00 `
  --end 2026-02-10T23:59:59
```

JSON output (for scripts):
```bash
python -m src.cli list --json
```

### Add an Outcome
```bash
python -m src.cli add-outcome `
  --decision-id <decision-id> `
  --outcome "Success" `
  --outcome-storage-path data/outcomes.json
```

Outcomes are append-only.

### List Outcomes
```bash
python -m src.cli list-outcomes
```

Filter by decision:
```bash
python -m src.cli list-outcomes --decision-id <id>
```

JSON mode:
```bash
python -m src.cli list-outcomes --json
```
### Stats

Human-readable:
```bash
python -m src.cli stats
```

JSON:
```bash
python -m src.cli stats --json
```

```bash
python -m src.cli stats `
  --outcome-storage-path data/outcomes.json
```

JSON mode:
```bash
python -m src.cli stats `
  --outcome-storage-path data/outcomes.json `
  --json
```

Example JSON output:
```bash
{
  "total_decisions": 5,
  "total_outcomes": 3,
  "by_actor": {
    "alice": 2,
    "bob": 3
  },
  "by_tag": {
    "database": 2,
    "ml": 1
  }
}
```

### Export to CSV
```bash
python -m src.cli export `
  --format csv `
  --output data/export.csv
```

With filters:
```bash
python -m src.cli export `
  --format csv `
  --output data/export.csv `
  --actor alice `
  --start 2026-02-01T00:00:00 `
  --end 2026-02-10T23:59:59
```

## Design Tradeoffs

- JSON file storage instead of DB
- Linear scans instead of indexing
- No concurrency support
- No schema migrations yet
- No enforcement that an outcome must be terminal

This is intentional.
It optimizes for clarity and auditability over scale.

## Testing

Run:
```bash
pytest
```

Test coverage includes:
- Immutable decision invariants
- Append-only outcome validation
- CLI integration (end-to-end flow)
- JSON output correctness

## When To Use This

- Internal tools
- ML experiment tracking
- Engineering decisions
- Lightweight audit logging
- Personal or team reasoning logs

If you need high write concurrency or millions of records, use a database.

## License

MIT