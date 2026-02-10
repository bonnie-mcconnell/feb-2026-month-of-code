from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from .models import Decision
from .storage import load_all


def load_decisions(storage_path: Path) -> List[Decision]:
    decisions = load_all(storage_path)
    return sorted(decisions, key=lambda d: d.timestamp)


def filter_by_actor(decisions: Iterable[Decision], actor: str) -> List[Decision]:
    return [d for d in decisions if d.actor == actor]


def filter_by_tag(decisions: Iterable[Decision], tag: str) -> List[Decision]:
    return [d for d in decisions if tag in d.tags]


def filter_by_time_range(
    decisions: Iterable[Decision],
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[Decision]:
    def in_range(decision: Decision) -> bool:
        ts = datetime.fromisoformat(decision.timestamp)

        if start:
            if ts < datetime.fromisoformat(start):
                return False
        if end:
            if ts > datetime.fromisoformat(end):
                return False
        return True

    return [d for d in decisions if in_range(d)]


def search_text(decisions: Iterable[Decision], query: str) -> List[Decision]:
    q = query.lower()
    return [
        d
        for d in decisions
        if q in d.title.lower() or q in d.description.lower()
    ]
