from __future__ import annotations

import re
from typing import Dict, List

from decimal import Decimal

from .errors import InvoiceParseError


INVOICE_NUMBER_RE = re.compile(r"Invoice\s*#?\s*[:\-]?\s*(\S+)", re.IGNORECASE)
DATE_RE = re.compile(r"Date\s*[:\-]?\s*(.+)", re.IGNORECASE)
MONEY_RE = re.compile(r"\$?\s*([0-9,]+\.\d{2})")


def extract_invoice_number(header_lines: List[str]) -> str:
    for line in header_lines:
        match = INVOICE_NUMBER_RE.search(line)
        if match:
            return match.group(1)

    raise InvoiceParseError(
        "Invoice number not found",
        "FIELD_NOT_FOUND",
    )


def extract_invoice_date(header_lines: List[str]) -> str:
    for line in header_lines:
        match = DATE_RE.search(line)
        if match:
            return match.group(1).strip()

    raise InvoiceParseError(
        "Invoice date not found",
        "FIELD_NOT_FOUND",
    )


def extract_totals(totals_lines: List[str]) -> Dict[str, Decimal]:
    totals: Dict[str, Decimal] = {}

    for line in totals_lines:
        lower = line.lower()

        money_match = MONEY_RE.search(line)
        if not money_match:
            continue

        amount = Decimal(money_match.group(1).replace(",", ""))

        if "subtotal" in lower:
            totals["subtotal"] = amount
        elif "tax" in lower:
            totals["tax"] = amount
        elif "total" in lower:
            totals["total"] = amount

    if "total" not in totals:
        raise InvoiceParseError(
            "Final total not found",
            "FIELD_NOT_FOUND",
        )

    return totals