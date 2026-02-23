from decimal import Decimal
from pathlib import Path

from invoice_extractor.services.extractor_services import (
    extract_invoice_from_pdf,
)
from invoice_extractor.domain.validation import validate_invoice


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_invoice_1.pdf"


def test_real_pdf_extraction() -> None:
    invoice = extract_invoice_from_pdf(FIXTURE_PATH)

    validate_invoice(invoice)

    assert invoice.invoice_number == "INV-001"
    assert invoice.total.amount == Decimal("220.00")
    assert invoice.currency == "USD"