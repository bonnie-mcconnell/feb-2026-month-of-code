import pytest

from invoice_extractor.parsing.strategies.registry import StrategyRegistry
from invoice_extractor.parsing.errors import InvoiceParseError


def test_registry_unsupported_vendor() -> None:
    registry = StrategyRegistry()

    with pytest.raises(InvoiceParseError):
        registry.resolve(["Completely Unknown Vendor Format"])