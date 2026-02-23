from decimal import Decimal

from invoice_extractor.services.extractor_services import (
    extract_invoice_from_lines,
)
from invoice_extractor.domain.validation import validate_invoice


def test_full_pipeline_valid_invoice() -> None:
    lines = [
        "Invoice #123",
        "Date: 2026-02-01",
        "Description Qty Total",
        "Widget A 2 100.00 200.00",
        "Subtotal 200.00",
        "Tax 20.00",
        "Total 220.00",
    ]

    invoice = extract_invoice_from_lines(lines)

    validate_invoice(invoice)

    assert invoice.invoice_number == "123"
    assert invoice.total.amount == Decimal("220.00")