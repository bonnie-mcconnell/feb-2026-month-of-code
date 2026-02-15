from datetime import datetime
from src.models import NewsItem
from src.engine import score_items
from src.aggregator import Aggregator
from src.sector import load_sector_weights

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

    # Weighted avg
    sector_weights = load_sector_weights()
    weight = sector_weights.get("AAPL", 1.0)
    expected_avg = sum(s.score for s in scored) / len(scored) * weight

    assert round(day.avg_score, 4) == round(expected_avg, 4)
