from datetime import datetime
import json
from pathlib import Path
import tempfile

import pytest
from src.repository import Repository
from src.ingest import ingest
from src.engine import run_pipeline
from src.models import DailyAggregate, NewsItem

SAMPLE_JSON = [
    {"ticker": "AAPL", "headline": "Strong growth reported", "source": "Reuters", "published_at": "2024-02-01T09:00:00"},
    {"ticker": "AAPL", "headline": "Earnings miss guidance", "source": "Bloomberg", "published_at": "2024-02-01T10:00:00"},
    {"ticker": "MSFT", "headline": "Surge in cloud revenue", "source": "Reuters", "published_at": "2024-02-01T11:00:00"},
]

@pytest.fixture
def temp_repo():
    repo = Repository(db_path=":memory:")
    return repo

def test_ingest_raw_news(temp_repo, tmp_path):
    # Write sample JSON to temp file
    json_file = tmp_path / "sample.json"
    with open(json_file, "w") as f:
        json.dump(SAMPLE_JSON, f)

    # Run ingestion
    ingest(json_file, temp_repo)

    # Check raw_news count
    raw_rows = temp_repo.fetch_all_raw_news()
    assert len(raw_rows) == 3

    # Duplicate insert returns None
    duplicate_id = temp_repo.insert_raw_news("AAPL", "Strong growth reported", "Reuters", "2024-02-01T09:00:00")
    assert duplicate_id is None

def test_scored_news_insertion(temp_repo):
    # Insert raw news
    raw_id = temp_repo.insert_raw_news("AAPL", "Strong growth reported", "Reuters", "2024-02-01T09:00:00")
    assert raw_id is not None

    # Insert scored news
    score_id = temp_repo.insert_scored_news(raw_id, 1)
    assert score_id is not None

    # Fetch scored_news
    scored_rows = temp_repo.fetch_scored_news_since()
    assert len(scored_rows) == 1
    assert scored_rows[0]["score"] == 1

    
def test_daily_aggregate_upsert(temp_repo, tmp_path):
    # Insert scored news manually
    raw_id1 = temp_repo.insert_raw_news("AAPL", "Strong growth", "Reuters", "2024-02-01T09:00:00")
    raw_id2 = temp_repo.insert_raw_news("AAPL", "Earnings miss", "Bloomberg", "2024-02-01T10:00:00")
    temp_repo.insert_scored_news(raw_id1, 1)
    temp_repo.insert_scored_news(raw_id2, -1)

    # Create empty dummy JSON file
    dummy_file = tmp_path / "dummy.json"
    dummy_file.write_text("[]")

    # Aggregate manually
    news_items = run_pipeline(str(dummy_file), repo=temp_repo)

    day = news_items["AAPL"]["2024-02-01"]

    assert isinstance(day, DailyAggregate)
    assert day.volume == 2
    expected_avg = sum([1, -1]) / 2
    assert round(day.avg_score, 4) == round(expected_avg, 4)
    assert day.positive_ratio == 0.5
    assert day.negative_ratio == 0.5
