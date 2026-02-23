from datetime import datetime, date
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


def _parse_date(date_str: str) -> date:
    return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()


class DefaultInvoiceParser(InvoiceParserStrategy):

    def can_parse(self, lines: List[str]) -> bool:
        return any("Invoice" in line for line in lines)

    def parse(self, lines: List[str]) -> Invoice:

        segmented = segment_invoice(lines)

        invoice_number = extract_invoice_number(segmented.header_lines)
        invoice_date_str = extract_invoice_date(segmented.header_lines)
        invoice_date = _parse_date(invoice_date_str)

        line_items = parse_line_items(segmented.line_item_lines)

        if not line_items:
            raise ValueError("Invoice must contain at least one line item.")

        totals_dict = extract_totals(segmented.totals_lines)

        currency = line_items[0].currency()

        subtotal = Money(
            totals_dict.get("subtotal", totals_dict["total"]),
            currency,
        )

        tax = (
            Money(totals_dict["tax"], currency)
            if "tax" in totals_dict
            else Money("0.00", currency)
        )

        total = Money(totals_dict["total"], currency)

        return Invoice(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=invoice_date,
            vendor=Vendor(name="UNKNOWN"),
            customer=Customer(name="UNKNOWN"),
            currency=currency,
            line_items=line_items,
            subtotal=subtotal,
            tax=tax,
            total=total,
        )