import pytest
from decimal import Decimal
from datetime import date

from invoice_extractor.domain.invoice import Invoice, Vendor, Customer
from invoice_extractor.domain.line_item import LineItem
from invoice_extractor.domain.money import Money
from invoice_extractor.domain.validation import (
    validate_invoice,
    InvoiceValidationError,
)


# -------------------------
# Helpers
# -------------------------

def make_valid_invoice() -> Invoice:
    item = LineItem(
        description="Consulting",
        quantity=Decimal("2"),
        unit_price=Money("100.00", "USD"),
        total=Money("200.00", "USD"),
    )

    return Invoice(
        invoice_number="INV-001",
        invoice_date=date(2025, 1, 1),
        due_date=date(2025, 2, 1),
        vendor=Vendor(name="Acme Corp", address="123 Road"),
        customer=Customer(name="Client LLC"),
        currency="USD",
        line_items=[item],
        subtotal=Money("200.00", "USD"),
        tax=Money("20.00", "USD"),
        total=Money("220.00", "USD"),
    )


# -------------------------
# Happy Path
# -------------------------

def test_valid_invoice_passes() -> None:
    invoice = make_valid_invoice()
    validate_invoice(invoice)  # should not raise


# -------------------------
# Line Item Validation
# -------------------------

def test_line_item_total_mismatch() -> None:
    invoice = make_valid_invoice()
    invoice.line_items[0].total = Money("199.99", "USD")

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "LINE_ITEM_TOTAL_MISMATCH"


def test_invalid_quantity_zero() -> None:
    invoice = make_valid_invoice()
    invoice.line_items[0].quantity = Decimal("0")

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "INVALID_QUANTITY"


# -------------------------
# Subtotal/Total Reconciliation
# -------------------------

def test_subtotal_mismatch() -> None:
    invoice = make_valid_invoice()
    invoice.subtotal = Money("999.00", "USD")

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "SUBTOTAL_MISMATCH"


def test_total_mismatch() -> None:
    invoice = make_valid_invoice()
    invoice.total = Money("999.00", "USD")

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "TOTAL_MISMATCH"


# -------------------------
# Currency Consistency
# -------------------------

def test_line_item_currency_mismatch() -> None:
    invoice = make_valid_invoice()
    invoice.line_items[0].unit_price = Money("100.00", "EUR")

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "CURRENCY_MISMATCH"


def test_invoice_total_currency_mismatch() -> None:
    invoice = make_valid_invoice()
    invoice.total = Money("220.00", "EUR")

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "CURRENCY_MISMATCH"


# -------------------------
# Negative Amounts
# -------------------------

def test_negative_unit_price() -> None:
    invoice = make_valid_invoice()
    invoice.line_items[0].unit_price = Money("-100.00", "USD")

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "NEGATIVE_AMOUNT"


def test_negative_invoice_total() -> None:
    invoice = make_valid_invoice()
    invoice.total = Money("-220.00", "USD")

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "NEGATIVE_AMOUNT"


# -------------------------
# Required Fields
# -------------------------

def test_missing_invoice_number() -> None:
    invoice = make_valid_invoice()
    invoice.invoice_number = ""

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "MISSING_FIELD"


def test_missing_line_items() -> None:
    invoice = make_valid_invoice()
    invoice.line_items = []

    with pytest.raises(InvoiceValidationError) as exc:
        validate_invoice(invoice)

    assert exc.value.code == "MISSING_LINE_ITEMS"