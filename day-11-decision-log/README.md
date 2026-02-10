# Decision Log/Audit Trail System

A small, focused system for recording, persisting, and reviewing decisions made by humans or automated processes.  
Designed for engineering accountability, auditability, and temporal reasoning.

---

## What This System Does

- Records **immutable decisions** with context, rationale, tradeoffs, and optional tags.
- Persists all decisions in an **append-only JSON log**.
- Provides **read-only query functions** for filtering by actor, tag, or time.
- Offers a **minimal CLI** to add and list decisions.

This is **not a generic CRUD app**. It’s an audit-focused tool for situations where **history matters**.

---

## Who This Is For

- Engineers maintaining complex pipelines or internal tooling.
- Teams needing to track **why decisions were made**, not just the outcome.
- Regulated environments where **accountability and transparency** are required.

---

## Problem It Solves

Decisions in engineering and data environments often:

- Lack context
- Are forgotten
- Have no auditable trail

This system provides a **trusted, transparent record**:

- Who made the decision  
- When it was made  
- What inputs and options were considered  
- Known tradeoffs  

All in a format that’s **human-readable** and **Git-friendly**.

---

## Key Design Decisions

1. **Immutable Decision Model**
   - `Decision` objects are frozen dataclasses.
   - IDs and timestamps are auto-generated.
   - Prevents accidental mutation.

2. **Append-Only Storage**
   - `decisions.json` is rewritten on append.
   - No updates or deletes allowed.
   - Guarantees a complete, auditable history.

3. **Thin Logging API**
   - `log.py` is the single, trusted path to record decisions.
   - Prevents bypassing validation or storage rules.

4. **Read-Only Query Layer**
   - Functions to filter by actor, tag, time range, or keyword.
   - Maintains temporal ordering.
   - No mutation or hidden side-effects.

5. **Minimal CLI**
   - Only adds and lists decisions.
   - No editing, deleting, or outcome updates.

6. **High Signal, Low Friction**
   - No unnecessary dependencies
   - No over-engineering
   - Clear, boring, auditable

---

## Known Limitations

- Concurrent writers not supported (rewrites full file)
- No schema versioning
- No deep input validation beyond JSON-serializable dictionary
- No outcome tracking (optional future extension)
- Queries are linear scans (fine for small/medium logs)

---

## Potential Improvements

- Versioned schema and backward compatibility
- Outcome updates without mutation (immutable append pattern)
- Export to CSV for dashboards
- Lightweight metrics (counts, categories, actors)
- Optional indexing for very large logs

These are optional and could be added if this system grows in production.

---

## Project Layout

```text
day-11-decision-log/
├── README.md
├── src/
│ ├── models.py # Immutable decision model with validation
│ ├── storage.py # Append-only JSON persistence
│ ├── log.py # Single API for recording decisions
│ ├── query.py # Read-only query helpers
│ └── cli.py # Minimal CLI
├── tests/
│ └── test_decisions.py # High-value invariants tests
└── data/
└── decisions.json # Append-only decision log
```

---

## Usage Examples

### Add a decision (CLI)
```bash
python -m src.cli add \
  --actor "alice" \
  --title "Choose database" \
  --description "Decided to use SQLite for simplicity" \
  --context "Prototype stage" \
  --inputs '{"options":["Postgres","SQLite"],"constraints":["dev environment"]}' \
  --options SQLite Postgres \
  --tradeoffs "SQLite easier for local dev, not scalable" \
  --tags database prototype
```

### List decisions (CLI)
```bash
python -m src.cli list --actor alice
```

### Programmatic use
```bash
from pathlib import Path
from src.log import record_decision
from src.query import load_decisions, filter_by_tag

path = Path("data/decisions.json")

record_decision(
    actor="bob",
    title="Select ML model",
    description="Chose random forest for interpretability",
    context="ML pipeline",
    inputs={"options": ["RF", "XGBoost"]},
    storage_path=path
)

decisions = load_decisions(path)
important = filter_by_tag(decisions, "high-priority")
```

## License & Attribution

MIT License - no external dependencies beyond Python standard library (and pytest for tests).