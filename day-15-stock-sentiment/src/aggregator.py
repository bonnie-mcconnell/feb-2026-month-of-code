from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Sequence

from .models import ScoredNews, DailyAggregate
from .scorer import classify
from .repository import Repository
from .sector import load_sector_weights


class Aggregator:
    """
    Handles aggregation of scored news into daily aggregates.
    """

    def __init__(self, repo: Repository):
        self.repo = repo

    def aggregate_all(self) -> Dict[str, Dict[str, DailyAggregate]]:
        """
        Aggregate all scored_news in the DB.
        Returns ticker -> date -> DailyAggregate
        """
        scored_rows = self.repo.fetch_scored_news_since(last_id=None)
        items: List[ScoredNews] = []

        for row in scored_rows:
            raw = self.repo.fetch_raw_by_id(row["raw_id"])


            if raw:
                # Fix: include 'source' when creating ScoredNews
                items.append(
                    ScoredNews(
                        ticker=raw["ticker"],
                        headline=raw["headline"],
                        source=raw["source"],
                        published_at=datetime.fromisoformat(raw["published_at"]),
                        score=row["score"],
                    )
                )

        return self._aggregate_items(items)

    @staticmethod
    def _aggregate_items(items: List[ScoredNews]) -> Dict[str, Dict[str, DailyAggregate]]:
        sector_weights = load_sector_weights()

        grouped = defaultdict(lambda: defaultdict(list))
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
                positive_count = sum(1 for e in entries if classify(e.score) == "positive")
                negative_count = sum(1 for e in entries if classify(e.score) == "negative")

                base_avg = total_score / volume
                weight = sector_weights.get(ticker, 1.0)
                avg_score = base_avg * weight

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
    

    @staticmethod
    def compute_rolling_average(
        aggregates: Sequence[DailyAggregate],
        window: int = 3
    ) -> list[float]:

        results = []

        for i in range(len(aggregates)):
            start = max(0, i - window + 1)
            window_slice = aggregates[start:i+1]
            avg = sum(a.avg_score for a in window_slice) / len(window_slice)
            results.append(avg)

        return results

