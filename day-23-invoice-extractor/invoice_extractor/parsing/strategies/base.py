from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from ...domain.invoice import Invoice


class InvoiceParserStrategy(ABC):
    """
    Deterministic invoice parsing strategy interface.
    """

    @abstractmethod
    def can_parse(self, lines: List[str]) -> bool:
        ...

    @abstractmethod
    def parse(self, lines: List[str]) -> Invoice:
        ...