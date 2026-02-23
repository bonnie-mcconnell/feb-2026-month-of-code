from dataclasses import dataclass
from datetime import datetime, timezone
from .money import Money


@dataclass(frozen=True)
class Ticker:
    exchange: str
    symbol: str
    bid: Money
    ask: Money
    timestamp: datetime

    def __post_init__(self):
        if self.ask < self.bid:
            raise ValueError("Ask price cannot be lower than bid price")

        if self.timestamp.tzinfo is None or self.timestamp.tzinfo != timezone.utc:
            raise ValueError("Timestamp must be timezone-aware UTC")