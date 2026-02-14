from typing import Dict, List

from .models import NewsItem, ScoredNews, DailyAggregate
from .loader import load_news
from .scorer import score_headline
from .aggregator import aggregate_daily


def score_items(items: List[NewsItem]) -> List[ScoredNews]:
    scored: List[ScoredNews] = []

    for item in items:
        score = score_headline(item.headline)

        scored.append(
            ScoredNews(
                ticker=item.ticker,
                headline=item.headline,
                source=item.source,
                published_at=item.published_at,
                score=score,
            )
        )

    return scored


def run_pipeline(
    path: str,
) -> Dict[str, Dict[str, DailyAggregate]]:
    news_items = load_news(path)

    scored_items = score_items(news_items)

    aggregated = aggregate_daily(scored_items)

    return aggregated
