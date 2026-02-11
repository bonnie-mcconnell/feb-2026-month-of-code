from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import json
import uuid
import tempfile
import os

def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _validate_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


@dataclass(frozen=True)
class Outcome:
    outcome_id: str
    decision_id: str
    timestamp: str
    outcome: str
    notes: Optional[str] = None

    @staticmethod
    def create(
        *,
        decision_id: str,
        outcome: str,
        notes: Optional[str] = None,
    ) -> "Outcome":
        _validate_non_empty(decision_id, "decision_id")
        _validate_non_empty(outcome, "outcome")

        if notes is not None and not isinstance(notes, str):
            raise ValueError("notes must be a string if provided")

        return Outcome(
            outcome_id=str(uuid.uuid4()),
            decision_id=decision_id,
            timestamp=_utc_now_iso(),
            outcome=outcome,
            notes=notes,
        )

    def to_dict(self) -> dict:
        return {
            "outcome_id": self.outcome_id,
            "decision_id": self.decision_id,
            "timestamp": self.timestamp,
            "outcome": self.outcome,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "Outcome":
        return Outcome(**data)


# ---- Storage (append-only) ----

def load_all(path: Path) -> List[Outcome]:
    if not path.exists():
        return []

    raw = path.read_text()
    if not raw.strip():
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse outcome log: {path}") from e

    if not isinstance(data, list):
        raise RuntimeError("Outcome log must be a list of records")

    return [Outcome.from_dict(item) for item in data]


def append(outcome: Outcome, path: Path) -> None:
    outcomes = load_all(path)
    outcomes.append(outcome)

    serialized = [o.to_dict() for o in outcomes]

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as tmp:
        tmp.write(json.dumps(serialized, indent=2))
        tmp_path = tmp.name

    os.replace(tmp_path, path)


# ---- Query helpers ----

def filter_by_decision(
    outcomes: List[Outcome],
    decision_id: str,
) -> List[Outcome]:
    return [o for o in outcomes if o.decision_id == decision_id]


def filter_by_time_range(
    outcomes: List[Outcome],
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[Outcome]:
    def in_range(o: Outcome) -> bool:
        ts = datetime.fromisoformat(o.timestamp)

        if start and ts < datetime.fromisoformat(start):
            return False
        if end and ts > datetime.fromisoformat(end):
            return False

        return True

    return [o for o in outcomes if in_range(o)]


def search_text(
    outcomes: List[Outcome],
    query: str,
) -> List[Outcome]:
    q = query.lower()

    return [
        o
        for o in outcomes
        if q in o.outcome.lower()
        or (o.notes and q in o.notes.lower())
    ]
