from collections import defaultdict
from typing import Dict, List

from .models import ScoredNews, DailyAggregate
from .scorer import classify


def aggregate_daily(
    items: List[ScoredNews],
) -> Dict[str, Dict[str, DailyAggregate]]:
    grouped = defaultdict(lambda: defaultdict(list))

    # Group by ticker and date
    for item in items:
        date_str = item.published_at.date().isoformat()
        grouped[item.ticker][date_str].append(item)

    results: Dict[str, Dict[str, DailyAggregate]] = {}

    for ticker, date_map in grouped.items():
        results[ticker] = {}

        for date_str, entries in date_map.items():
            volume = len(entries)

            if volume == 0:
                continue

            total_score = sum(e.score for e in entries)

            positive_count = 0
            negative_count = 0

            for e in entries:
                label = classify(e.score)
                if label == "positive":
                    positive_count += 1
                elif label == "negative":
                    negative_count += 1

            avg_score = total_score / volume
            positive_ratio = positive_count / volume
            negative_ratio = negative_count / volume

            results[ticker][date_str] = DailyAggregate(
                ticker=ticker,
                date=date_str,
                avg_score=avg_score,
                volume=volume,
                positive_ratio=positive_ratio,
                negative_ratio=negative_ratio,
            )

    return results
