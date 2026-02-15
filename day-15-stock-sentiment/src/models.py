from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class NewsItem:
    ticker: str
    headline: str
    source: str
    published_at: datetime


@dataclass
class ScoredNews:
    ticker: str
    headline: str
    source: str
    published_at: datetime
    score: float


@dataclass
class DailyAggregate:
    ticker: str
    date: str  # YYYY-MM-DD
    avg_score: float
    volume: int
    positive_ratio: float
    negative_ratio: float

    def to_dict(self) -> Dict:
        return {
            "ticker": self.ticker,
            "date": self.date,
            "avg_score": self.avg_score,
            "volume": self.volume,
            "positive_ratio": self.positive_ratio,
            "negative_ratio": self.negative_ratio,
        }
