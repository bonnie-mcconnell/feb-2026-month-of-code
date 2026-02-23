import pytest

from invoice_extractor.parsing.segmenter import segment_invoice
from invoice_extractor.parsing.errors import InvoiceParseError

def make_valid_lines() -> list[str]:
    return [
        "Acme Corp",
        "Invoice # INV-001",
        "",
        "Description   Qty   Unit Price   Total",
        "Consulting     2     100.00       200.00",
        "Subtotal: 200.00",
        "Tax: 20.00",
        "Total: 220.00",
    ]


def test_valid_segmentation() -> None:
    lines = make_valid_lines()
    segmented = segment_invoice(lines)

    assert len(segmented.header_lines) > 0
    assert len(segmented.line_item_lines) > 1
    assert len(segmented.totals_lines) > 0


def test_missing_table_header() -> None:
    lines = make_valid_lines()
    lines[3] = "Something else"

    with pytest.raises(InvoiceParseError) as exc:
        segment_invoice(lines)

    assert exc.value.code == "TABLE_HEADER_NOT_FOUND"


def test_missing_totals() -> None:
    lines = make_valid_lines()
    lines = lines[:-3]

    with pytest.raises(InvoiceParseError) as exc:
        segment_invoice(lines)

    assert exc.value.code == "TOTALS_NOT_FOUND"


def test_totals_before_header() -> None:
    lines = make_valid_lines()
    lines.insert(0, "Subtotal: 200.00")

    with pytest.raises(InvoiceParseError) as exc:
        segment_invoice(lines)

    assert exc.value.code == "UNSUPPORTED_FORMAT"


def test_no_line_items() -> None:
    lines = [
        "Acme Corp",
        "Description   Qty   Unit Price   Total",
        "Subtotal: 200.00",
    ]

    with pytest.raises(InvoiceParseError) as exc:
        segment_invoice(lines)

    assert exc.value.code == "NO_LINE_ITEMS"