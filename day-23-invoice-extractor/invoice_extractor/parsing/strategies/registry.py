from typing import List

from .base import InvoiceParserStrategy
from .default_strategy import DefaultInvoiceParser


class StrategyRegistry:

    def __init__(self) -> None:
        self._strategies: List[InvoiceParserStrategy] = [
            DefaultInvoiceParser(),
        ]

    def resolve(self, lines: List[str]) -> InvoiceParserStrategy:
        for strategy in self._strategies:
            if strategy.can_parse(lines):
                return strategy

        raise ValueError("No suitable invoice parser found.")