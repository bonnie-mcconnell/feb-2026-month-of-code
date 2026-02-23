from __future__ import annotations

import re
from typing import List
from decimal import Decimal, InvalidOperation

from ..domain.line_item import LineItem
from ..domain.money import Money
from .errors import InvoiceParseError


LINE_ITEM_RE = re.compile(
    r"""
    ^(?P<description>.+?)\s+
    (?P<quantity>\d+(?:\.\d+)?)\s+
    \$?(?P<unit_price>\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s+
    \$?(?P<total>\d{1,3}(?:,\d{3})*(?:\.\d{2}))
    $
    """,
    re.VERBOSE,
)


def parse_line_items(table_lines: List[str]) -> List[LineItem]:
    """
    Deterministic line item parsing.

    Expected row format:
        Description <space> Quantity <space> UnitPrice <space> Total

    Example:
        Consulting Services 2 1500.00 3000.00
    """

    if len(table_lines) < 2:
        raise InvoiceParseError(
            "Line item table is empty",
            "TABLE_PARSE_ERROR",
        )

    rows = table_lines[1:]
    items: List[LineItem] = []

    for row in rows:
        stripped = row.strip()
        if not stripped:
            continue

        match = LINE_ITEM_RE.match(stripped)
        if not match:
            raise InvoiceParseError(
                f"Malformed line item row: {row}",
                "TABLE_PARSE_ERROR",
            )

        try:
            quantity = Decimal(match.group("quantity"))
            unit_price_value = Decimal(match.group("unit_price").replace(",", ""))
            total_value = Decimal(match.group("total").replace(",", ""))
        except (InvalidOperation, ValueError):
            raise InvoiceParseError(
                f"Invalid numeric values in row: {row}",
                "TABLE_PARSE_ERROR",
            )

        unit_price = Money(unit_price_value, "USD")
        total = Money(total_value, "USD")

        items.append(
            LineItem(
                description=match.group("description"),
                quantity=quantity,
                unit_price=unit_price,
                total=total,
            )
        )

    if not items:
        raise InvoiceParseError(
            "No valid line items found",
            "TABLE_PARSE_ERROR",
        )

    return items