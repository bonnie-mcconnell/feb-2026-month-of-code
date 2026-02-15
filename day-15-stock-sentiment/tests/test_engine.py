from datetime import datetime
from src.models import NewsItem
from src.engine import score_items
from src.aggregator import Aggregator

# Helper for in-memory aggregation
def aggregate_daily(items):
    return Aggregator._aggregate_items(items)


def test_engine_scoring_and_aggregation_flow():
    items = [
        NewsItem("AAPL", "Strong growth", "src", datetime(2024, 2, 1, 9)),
        NewsItem("AAPL", "Earnings miss", "src", datetime(2024, 2, 1, 10)),
    ]

    scored = score_items(items)
    aggregated = aggregate_daily(scored)

    day = aggregated["AAPL"]["2024-02-01"]

    assert day.volume == 2
    assert day.avg_score == 0.5  # +1 and -1
