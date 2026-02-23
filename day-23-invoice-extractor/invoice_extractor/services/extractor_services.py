from __future__ import annotations

from pathlib import Path
from datetime import datetime, date

from ..parsing.text_extractor import extract_text_lines
from ..parsing.segmenter import segment_invoice
from ..parsing.field_mapper import (
    extract_invoice_number,
    extract_invoice_date,
    extract_totals,
)
from ..parsing.line_item_parser import parse_line_items

from ..domain.invoice import Invoice, Vendor, Customer
from ..domain.money import Money


def _parse_date(date_str: str) -> date:
    """
    Deterministic ISO-style parsing.
    Adjust format if invoice format changes.
    """
    return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()


def extract_invoice_from_pdf(pdf_path: Path) -> Invoice:
    lines = extract_text_lines(pdf_path)

    header_lines, table_lines, totals_lines = segment_invoice(lines)

    invoice_number = extract_invoice_number(header_lines)
    invoice_date_str = extract_invoice_date(header_lines)
    invoice_date = _parse_date(invoice_date_str)

    # Temporary deterministic fallback
    due_date = invoice_date

    line_items = parse_line_items(table_lines)

    totals_dict = extract_totals(totals_lines)

    if not line_items:
        raise ValueError("Invoice must contain at least one line item.")

    currency = line_items[0].currency()

    subtotal = Money(totals_dict.get("subtotal", totals_dict["total"]), currency)

    tax = (
        Money(totals_dict["tax"], currency)
        if "tax" in totals_dict
        else Money("0.00", currency)
    )

    total = Money(totals_dict["total"], currency)

    return Invoice(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        vendor=Vendor(name="UNKNOWN"),
        customer=Customer(name="UNKNOWN"),
        currency=currency,
        line_items=line_items,
        subtotal=subtotal,
        tax=tax,
        total=total,
    )