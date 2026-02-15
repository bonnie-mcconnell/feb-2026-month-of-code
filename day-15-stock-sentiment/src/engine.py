from typing import Dict, List, Optional

from .models import NewsItem, ScoredNews, DailyAggregate
from .loader import load_news
from .scorer import score_headline
from .aggregator import Aggregator
from .repository import Repository


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


def run_pipeline(path: str, repo: Optional[Repository] = None) -> Dict[str, Dict[str, DailyAggregate]]:
    """
    Run full pipeline:
    load -> score -> aggregate -> store
    """
    news_items = load_news(path)
    scored_items = score_items(news_items)

    # If repo not passed, create in-memory for this run
    if repo is None:
        repo = Repository()

    # Upsert scored news into DB
    for item in scored_items:
        raw_id = repo.insert_raw_news(
            ticker=item.ticker,
            headline=item.headline,
            source=item.source,
            published_at=item.published_at.isoformat(),
        )
        if raw_id is not None:
            repo.insert_scored_news(raw_id=raw_id, score=item.score)

    # Aggregate everything
    aggregator = Aggregator(repo)
    aggregated = aggregator.aggregate_all()

    return aggregated
