from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from .errors import InvoiceParseError


@dataclass(slots=True)
class SegmentedInvoice:
    header_lines: List[str]
    line_item_lines: List[str]
    totals_lines: List[str]


TABLE_HEADER_REQUIRED_TERMS = ("description", "total")
QTY_TERMS = ("qty", "quantity")


def segment_invoice(lines: List[str]) -> SegmentedInvoice:
    """
    Deterministically segment invoice text into:
    - header block
    - line items block
    - totals block
    """

    header_idx = _find_table_header_index(lines)
    totals_idx = _find_totals_start_index(lines)

    if header_idx is None:
        raise InvoiceParseError(
            "Table header not found",
            "TABLE_HEADER_NOT_FOUND",
        )

    if totals_idx is None:
        raise InvoiceParseError(
            "Subtotal line not found",
            "TOTALS_NOT_FOUND",
        )

    if totals_idx <= header_idx:
        raise InvoiceParseError(
            "Totals block appears before line items",
            "UNSUPPORTED_FORMAT",
        )

    header_lines = lines[:header_idx]
    line_item_lines = lines[header_idx:totals_idx]
    totals_lines = lines[totals_idx:]

    if len(line_item_lines) <= 1:
        raise InvoiceParseError(
            "No line items detected",
            "NO_LINE_ITEMS",
        )

    return SegmentedInvoice(
        header_lines=header_lines,
        line_item_lines=line_item_lines,
        totals_lines=totals_lines,
    )


# -------------------------
# Internal helpers
# -------------------------

def _find_table_header_index(lines: List[str]) -> int | None:
    for idx, line in enumerate(lines):
        lower = line.lower()

        if all(term in lower for term in TABLE_HEADER_REQUIRED_TERMS):
            if any(q in lower for q in QTY_TERMS):
                return idx

    return None


def _find_totals_start_index(lines: List[str]) -> int | None:
    subtotal_pattern = re.compile(r"^\s*subtotal\b", re.IGNORECASE)

    for idx, line in enumerate(lines):
        if subtotal_pattern.search(line):
            return idx

    return None