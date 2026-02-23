import pytest

from invoice_extractor.parsing.line_item_parser import parse_line_items
from invoice_extractor.parsing.errors import InvoiceParseError


def test_line_item_malformed_row() -> None:
    lines = [
        "Description Qty Unit Price Total",
        "BadRowWithoutNumbers",
    ]

    with pytest.raises(InvoiceParseError):
        parse_line_items(lines)