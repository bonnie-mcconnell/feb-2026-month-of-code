# src/ingest.py
from pathlib import Path
import json
import csv
from datetime import datetime
from typing import List

from .models import NewsItem, ScoredNews
from .scorer import score_headline
from .repository import Repository


def load_json(path: Path) -> List[NewsItem]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = []
    for d in data:
        items.append(
            NewsItem(
                ticker=d["ticker"],
                headline=d["headline"],
                source=d["source"],
                published_at=datetime.fromisoformat(d["published_at"]),
            )
        )
    return items


def load_csv(path: Path) -> List[NewsItem]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(
                NewsItem(
                    ticker=row["ticker"],
                    headline=row["headline"],
                    source=row["source"],
                    published_at=datetime.fromisoformat(row["published_at"]),
                )
            )
    return items


def ingest(path: Path, repo: Repository):
    """
    Read JSON or CSV news file, score, and insert into DB.
    """
    if path.suffix.lower() == ".json":
        items = load_json(path)
    elif path.suffix.lower() == ".csv":
        items = load_csv(path)
    else:
        raise ValueError("Unsupported file format: only JSON or CSV allowed")

    for item in items:
        raw_id = repo.insert_raw_news(
            ticker=item.ticker,
            headline=item.headline,
            source=item.source,
            published_at=item.published_at.isoformat(),
        )
        if raw_id is not None:
            score = score_headline(item.headline)
            repo.insert_scored_news(raw_id=raw_id, score=score)
