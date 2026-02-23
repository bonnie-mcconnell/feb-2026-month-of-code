from __future__ import annotations

from typing import List

from .base import InvoiceParserStrategy
from .acme_strategy import AcmeInvoiceStrategy
from .default_strategy import DefaultInvoiceParser
from ..errors import InvoiceParseError


class StrategyRegistry:
    """
    Deterministic strategy resolution.

    Order matters:
    - Vendor-specific strategies first
    - Default fallback last
    """

    def __init__(self) -> None:
        self._strategies: List[InvoiceParserStrategy] = [
            AcmeInvoiceStrategy(),
            DefaultInvoiceParser(),  # fallback
        ]

    def resolve(self, lines: List[str]) -> InvoiceParserStrategy:
        for strategy in self._strategies:
            if strategy.can_parse(lines):
                return strategy

        raise InvoiceParseError(
            "No matching parsing strategy found",
            "UNSUPPORTED_VENDOR",
        )