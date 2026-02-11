import csv
from pathlib import Path
from typing import Iterable

from .models import Decision


def export_decisions_csv(decisions: Iterable[Decision], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "decision_id",
            "timestamp",
            "actor",
            "title",
            "description",
            "context",
            "tags",
        ])

        for d in decisions:
            writer.writerow([
                d.decision_id,
                d.timestamp,
                d.actor,
                d.title,
                d.description,
                d.context,
                ",".join(d.tags),
            ])
