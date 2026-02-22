from __future__ import annotations

from abc import ABC, abstractmethod
from tax_engine.domain.money import Money


class TaxCredit(ABC):
    @abstractmethod
    def apply(self, tax_due: Money) -> Money:
        """
        Return reduced tax after credit.
        """
        raise NotImplementedError