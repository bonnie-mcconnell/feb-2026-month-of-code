from __future__ import annotations

from abc import ABC, abstractmethod
from tax_engine.domain.money import Money


class TaxCredit(ABC):
    @abstractmethod
    def apply(self, tax_due: Money) -> Money:
        raise NotImplementedError


class FlatCredit(TaxCredit):
    def __init__(self, amount: Money) -> None:
        self.amount = amount

    def apply(self, tax_due: Money) -> Money:
        reduced = tax_due.subtract(self.amount)

        if reduced.is_negative():
            return Money.from_int(
                0,
                scale=tax_due.scale,
                rounding=tax_due.rounding,
            )

        return reduced