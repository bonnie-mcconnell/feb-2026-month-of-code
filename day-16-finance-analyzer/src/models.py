from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class Transaction:
    date: date
    description: str
    amount: Decimal
    category: Optional[str] = None

    @property
    def is_expense(self) -> bool:
        return self.amount < 0

    @property
    def is_income(self) -> bool:
        return self.amount > 0
