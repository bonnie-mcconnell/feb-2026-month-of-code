import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List

from .models import NewsItem


REQUIRED_FIELDS = {"ticker", "headline", "source", "published_at"}


def load_news(path: str) -> List[NewsItem]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"input file not found: {path}")

    if file_path.suffix.lower() == ".json":
        records = _load_json(file_path)
    elif file_path.suffix.lower() == ".csv":
        records = _load_csv(file_path)
    else:
        raise ValueError("unsupported file type (must be .json or .csv)")

    return [_parse_record(record) for record in records]


def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("json input must be a list of objects")

    return data


def _load_csv(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _parse_record(record: dict) -> NewsItem:
    if not REQUIRED_FIELDS.issubset(record.keys()):
        missing = REQUIRED_FIELDS - set(record.keys())
        raise ValueError(f"missing required fields: {missing}")

    try:
        published_at = datetime.fromisoformat(record["published_at"])
    except Exception:
        raise ValueError(
            f"invalid ISO timestamp: {record['published_at']}"
        )

    return NewsItem(
        ticker=record["ticker"].strip().upper(),
        headline=record["headline"].strip(),
        source=record["source"].strip(),
        published_at=published_at,
    )
