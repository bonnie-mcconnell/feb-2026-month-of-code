from dataclasses import dataclass
from decimal import Decimal
from .money import Money


@dataclass(frozen=True)
class Spread:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: Money
    sell_price: Money
    spread_absolute: Money
    spread_percent: Decimal