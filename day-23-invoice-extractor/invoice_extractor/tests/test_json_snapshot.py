import json
from pathlib import Path

from invoice_extractor.services.extractor_services import (
    extract_invoice_from_pdf,
)
from invoice_extractor.domain.validation import validate_invoice


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_invoice_1.pdf"


def test_invoice_json_snapshot() -> None:
    invoice = extract_invoice_from_pdf(FIXTURE_PATH)
    validate_invoice(invoice)

    result = invoice.to_dict()

    expected = {
        "invoice_number": "INV-001",
        "currency": "USD",
        "subtotal": "200.00",
        "tax": "20.00",
        "total": "220.00",
        "line_items": [
            {
                "description": "Widget A",
                "quantity": 2,
                "unit_price": "100.00",
                "total": "200.00",
            }
        ],
    }

    assert result == expected