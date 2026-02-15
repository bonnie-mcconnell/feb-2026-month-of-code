from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from .models import ScoredNews, DailyAggregate
from .scorer import classify
from .repository import Repository


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
            raw = self.repo.conn.execute(
                "SELECT * FROM raw_news WHERE id = ?", (row["raw_id"],)
            ).fetchone()

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
