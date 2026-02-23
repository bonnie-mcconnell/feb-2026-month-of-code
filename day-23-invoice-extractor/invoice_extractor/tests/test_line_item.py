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


def test_line_item_invalid_numeric() -> None:
    from invoice_extractor.parsing.line_item_parser import parse_line_items
    from invoice_extractor.parsing.errors import InvoiceParseError

    lines = [
        "Description Qty Unit Price Total",
        "Widget A X 100.00 200.00",
    ]

    with pytest.raises(InvoiceParseError):
        parse_line_items(lines)


def test_line_item_empty_input() -> None:
    with pytest.raises(InvoiceParseError) as exc:
        parse_line_items([])

    assert exc.value.code == "TABLE_PARSE_ERROR"