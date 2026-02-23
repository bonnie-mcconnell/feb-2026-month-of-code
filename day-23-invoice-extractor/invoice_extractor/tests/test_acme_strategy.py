import pytest
from invoice_extractor.parsing.strategies.acme_strategy import AcmeInvoiceStrategy
from invoice_extractor.parsing.errors import InvoiceParseError


def test_acme_can_parse_true() -> None:
    lines = ["ACME CORPORATION", "Invoice #123"]
    strategy = AcmeInvoiceStrategy()
    assert strategy.can_parse(lines) is True


def test_acme_can_parse_false() -> None:
    lines = ["Random Vendor"]
    strategy = AcmeInvoiceStrategy()
    assert strategy.can_parse(lines) is False


def test_acme_parse_invalid_format() -> None:
    strategy = AcmeInvoiceStrategy()

    with pytest.raises(InvoiceParseError):
        strategy.parse(["ACME CORPORATION"])


def test_acme_parse_happy_path() -> None:
    strategy = AcmeInvoiceStrategy()

    lines = [
        "ACME CORPORATION",
        "Invoice #INV-123",
        "Date: 2026-02-01",
        "Description Qty Unit Price Total",
        "Widget A 1 10.00 10.00",
        "Subtotal 10.00",
        "Tax 0.00",
        "Total 10.00",
    ]

    invoice = strategy.parse(lines)

    assert invoice.invoice_number == "INV-123"