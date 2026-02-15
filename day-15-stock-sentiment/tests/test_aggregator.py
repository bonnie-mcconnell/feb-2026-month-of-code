from datetime import datetime
from src.models import ScoredNews, DailyAggregate
from src.aggregator import Aggregator
from src.sector import load_sector_weights

# Helper to run in-memory aggregation without DB
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

    # Weighted average according to sector weights
    sector_weights = load_sector_weights()
    weight = sector_weights.get("AAPL", 1.0)
    expected_avg = sum(i.score for i in items) / len(items) * weight

    assert round(day.avg_score, 4) == round(expected_avg, 4)
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

    # Weighted averages
    sector_weights = load_sector_weights()
    weight = sector_weights.get("AAPL", 1.0)

    day1_avg = sum(i.score for i in items if i.published_at.date() == datetime(2024, 2, 1).date()) / 1 * weight
    day2_avg = sum(i.score for i in items if i.published_at.date() == datetime(2024, 2, 2).date()) / 1 * weight

    assert round(result["AAPL"]["2024-02-01"].avg_score, 4) == round(day1_avg, 4)
    assert round(result["AAPL"]["2024-02-02"].avg_score, 4) == round(day2_avg, 4)
