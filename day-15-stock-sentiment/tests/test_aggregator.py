from datetime import datetime
from src.models import ScoredNews, DailyAggregate
from src.aggregator import Aggregator

# Helper to run in-memory _aggregation without DB
def aggregate_daily(items):
    return Aggregator._aggregate_items(items)


def test_daily_aggregation_computes_correct_metrics():
    items = [
        ScoredNews("AAPL", "h1", "src", datetime(2024, 2, 1, 9), 1),
        ScoredNews("AAPL", "h2", "src", datetime(2024, 2, 1, 10), -1),
        ScoredNews("AAPL", "h3", "src", datetime(2024, 2, 1, 11), 1),
    ]

    result = aggregate_daily(items)
    day = result["AAPL"]["2024-02-01"]

    assert day.volume == 3
    assert day.avg_score == (1 - 1 + 1) / 3
    assert day.positive_ratio == 2 / 3
    assert day.negative_ratio == 1 / 3


def test_multiple_days_are_grouped_separately():
    items = [
        ScoredNews("AAPL", "h1", "src", datetime(2024, 2, 1, 9), 1),
        ScoredNews("AAPL", "h2", "src", datetime(2024, 2, 2, 9), -1),
    ]

    result = aggregate_daily(items)
    assert "2024-02-01" in result["AAPL"]
    assert "2024-02-02" in result["AAPL"]
    assert result["AAPL"]["2024-02-01"].avg_score == 1
    assert result["AAPL"]["2024-02-02"].avg_score == -1
