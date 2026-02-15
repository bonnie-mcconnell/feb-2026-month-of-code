from pathlib import Path
import json
import csv
from datetime import datetime
from typing import List

from .models import NewsItem
from .scorer import score_headline
from .repository import Repository
from .aggregator import Aggregator


def load_json(path: Path) -> List[NewsItem]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        NewsItem(
            ticker=d["ticker"],
            headline=d["headline"],
            source=d["source"],
            published_at=datetime.fromisoformat(d["published_at"]),
        )
        for d in data
    ]


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


def ingest(path: Path, repo: Repository) -> None:
    """
    Read JSON/CSV, score headlines, store in DB,
    then compute & persist daily aggregates.
    """
    if path.suffix.lower() == ".json":
        items = load_json(path)
    elif path.suffix.lower() == ".csv":
        items = load_csv(path)
    else:
        raise ValueError("Unsupported file format")

    for item in items:
        raw_id = repo.insert_raw_news(
            ticker=item.ticker,
            headline=item.headline,
            source=item.source,
            published_at=item.published_at.isoformat(),
        )

        if raw_id is not None:
            score = score_headline(item.headline)
            repo.insert_scored_news(raw_id, score)

    # Proper aggregation
    aggregator = Aggregator(repo)
    aggregates = aggregator.aggregate_all()

    for ticker_map in aggregates.values():
        for aggregate in ticker_map.values():
            repo.upsert_daily_aggregate(
                ticker=aggregate.ticker,
                date=aggregate.date,
                avg_score=aggregate.avg_score,
                volume=aggregate.volume,
                positive_ratio=aggregate.positive_ratio,
                negative_ratio=aggregate.negative_ratio,
            )