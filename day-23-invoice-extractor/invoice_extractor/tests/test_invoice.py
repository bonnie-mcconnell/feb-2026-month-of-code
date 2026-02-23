from datetime import date
from decimal import Decimal

from invoice_extractor.domain.invoice import Invoice, Vendor, Customer
from invoice_extractor.domain.money import Money
from invoice_extractor.domain.line_item import LineItem


def test_invoice_str_representation() -> None:
    item = LineItem(
        description="Test",
        quantity=Decimal("1"),
        unit_price=Money("10.00", "USD"),
        total=Money("10.00", "USD"),
    )

    invoice = Invoice(
        invoice_number="X",
        invoice_date=date(2026, 2, 1),
        due_date=date(2026, 2, 1),
        vendor=Vendor(name="ACME"),
        customer=Customer(name="Client"),
        currency="USD",
        line_items=[item],
        subtotal=Money("10.00", "USD"),
        tax=Money("0.00", "USD"),
        total=Money("10.00", "USD"),
    )

    result = str(invoice)

    assert "Invoice" in result
    assert "X" in result