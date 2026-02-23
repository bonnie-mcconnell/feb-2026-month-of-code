from __future__ import annotations

from datetime import datetime
from typing import List

from .base import InvoiceParserStrategy
from ..segmenter import segment_invoice
from ..field_mapper import (
    extract_invoice_number,
    extract_invoice_date,
    extract_totals,
)
from ..line_item_parser import parse_line_items
from ...domain.invoice import Invoice, Vendor, Customer
from ...domain.money import Money


class AcmeInvoiceStrategy(InvoiceParserStrategy):
    """
    Example vendor-specific strategy.
    """

    VENDOR_NAME = "ACME Corp"

    def can_parse(self, lines: List[str]) -> bool:
        return any(self.VENDOR_NAME.lower() in l.lower() for l in lines[:10])

    def parse(self, lines: List[str]) -> Invoice:
        segmented = segment_invoice(lines)

        invoice_number = extract_invoice_number(segmented.header_lines)
        date_str = extract_invoice_date(segmented.header_lines)
        invoice_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        line_items = parse_line_items(segmented.line_item_lines)
        totals_dict = extract_totals(segmented.totals_lines)

        currency = line_items[0].currency()

        subtotal = Money(totals_dict.get("subtotal", totals_dict["total"]), currency)
        tax = Money(totals_dict.get("tax", "0.00"), currency)
        total = Money(totals_dict["total"], currency)

        return Invoice(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=invoice_date,
            vendor=Vendor(name=self.VENDOR_NAME),
            customer=Customer(name="UNKNOWN"),
            currency=currency,
            line_items=line_items,
            subtotal=subtotal,
            tax=tax,
            total=total,
        )