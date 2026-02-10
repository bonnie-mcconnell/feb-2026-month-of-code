from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .models import Decision


def load_all(path: Path) -> List[Decision]:
    if not path.exists():
        return []

    try:
        raw = path.read_text()
        if not raw.strip():
            return []

        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse decision log: {path}") from e

    if not isinstance(data, list):
        raise RuntimeError("Decision log must be a list of records")

    return [Decision.from_dict(item) for item in data]


def append(decision: Decision, path: Path) -> None:
    decisions = load_all(path)
    decisions.append(decision)

    serialized = [d.to_dict() for d in decisions]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(serialized, indent=2))
