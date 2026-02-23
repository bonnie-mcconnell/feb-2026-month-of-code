import pytest

from invoice_extractor.parsing.field_mapper import extract_totals
from invoice_extractor.parsing.errors import InvoiceParseError


def test_extract_totals_missing_total() -> None:
    with pytest.raises(InvoiceParseError):
        extract_totals(["Subtotal 100.00"])