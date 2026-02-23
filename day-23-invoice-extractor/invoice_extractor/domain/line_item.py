from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .money import Money


@dataclass(slots=True)
class LineItem:
    description: str
    quantity: Decimal
    unit_price: Money
    total: Money

    def currency(self) -> str:
        return self.unit_price.currency