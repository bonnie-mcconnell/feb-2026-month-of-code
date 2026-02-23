from __future__ import annotations

from typing import List
from decimal import Decimal

from ..domain.line_item import LineItem
from .errors import InvoiceParseError
from ..domain.money import Money

def parse_line_items(table_lines: List[str]) -> List[LineItem]:
    if len(table_lines) < 2:
        raise InvoiceParseError(
            "Line item table is empty",
            "TABLE_PARSE_ERROR",
        )

    header = table_lines[0]
    rows = table_lines[1:]

    items: List[LineItem] = []

    for row in rows:
        tokens = row.split()

        if len(tokens) < 4:
            raise InvoiceParseError(
                f"Malformed line item row: {row}",
                "TABLE_PARSE_ERROR",
            )

        try:
            quantity = Decimal(tokens[-3])

            unit_price_value = Decimal(tokens[-2].replace("$", "").replace(",", ""))
            total_value = Decimal(tokens[-1].replace("$", "").replace(",", ""))

            unit_price = Money(unit_price_value, "USD")
            total = Money(total_value, "USD")
        except Exception:
            raise InvoiceParseError(
                f"Invalid numeric values in row: {row}",
                "TABLE_PARSE_ERROR",
            )

        description = " ".join(tokens[:-3])

        items.append(
            LineItem(
                description=description,
                quantity=quantity,
                unit_price=unit_price,
                total=total,
            )
        )

    return items