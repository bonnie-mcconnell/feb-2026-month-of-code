from __future__ import annotations

from typing import Iterable

from .invoice import Invoice
from .money import Money


class InvoiceValidationError(Exception):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


def validate_invoice(invoice: Invoice) -> None:
    """
    Deterministic validation pipeline.

    Order matters:
        1. Required fields
        2. Currency consistency
        3. Non-negative checks
        4. Line item math
        5. Invoice totals math
    """

    _validate_required_fields(invoice)
    _validate_currency_consistency(invoice)
    _validate_non_negative(invoice)
    _validate_line_items(invoice)
    _validate_totals(invoice)


# -------------------------
# Validation Steps
# -------------------------

def _validate_required_fields(invoice: Invoice) -> None:
    if not invoice.invoice_number:
        raise InvoiceValidationError(
            "Missing invoice number",
            "MISSING_FIELD",
        )

    if not invoice.line_items:
        raise InvoiceValidationError(
            "Invoice must contain at least one line item",
            "MISSING_LINE_ITEMS",
        )


def _validate_currency_consistency(invoice: Invoice) -> None:
    base_currency = invoice.currency.upper()

    for item in invoice.line_items:
        if item.unit_price.currency != base_currency:
            raise InvoiceValidationError(
                "Line item currency mismatch",
                "CURRENCY_MISMATCH",
            )

        if item.total.currency != base_currency:
            raise InvoiceValidationError(
                "Line item total currency mismatch",
                "CURRENCY_MISMATCH",
            )

    for money in (invoice.subtotal, invoice.tax, invoice.total):
        if money.currency != base_currency:
            raise InvoiceValidationError(
                "Invoice total currency mismatch",
                "CURRENCY_MISMATCH",
            )


def _validate_non_negative(invoice: Invoice) -> None:
    for item in invoice.line_items:
        if item.unit_price.is_negative():
            raise InvoiceValidationError(
                "Negative unit price not allowed",
                "NEGATIVE_AMOUNT",
            )

        if item.total.is_negative():
            raise InvoiceValidationError(
                "Negative line item total not allowed",
                "NEGATIVE_AMOUNT",
            )

        if item.quantity <= 0:
            raise InvoiceValidationError(
                "Line item has non-positive quantity",
                "INVALID_QUANTITY",
            )

    for money in (invoice.subtotal, invoice.tax, invoice.total):
        if money.is_negative():
            raise InvoiceValidationError(
                "Negative invoice amount not allowed",
                "NEGATIVE_AMOUNT",
            )


def _validate_line_items(invoice: Invoice) -> None:
    for item in invoice.line_items:
        expected_total = item.unit_price * item.quantity

        if expected_total != item.total:
            raise InvoiceValidationError(
                "Line item total mismatch",
                "LINE_ITEM_TOTAL_MISMATCH",
            )


def _validate_totals(invoice: Invoice) -> None:
    computed_subtotal = _sum_money(
        item.total for item in invoice.line_items
    )

    if computed_subtotal != invoice.subtotal:
        raise InvoiceValidationError(
            "Subtotal mismatch",
            "SUBTOTAL_MISMATCH",
        )

    computed_total = invoice.subtotal + invoice.tax

    if computed_total != invoice.total:
        raise InvoiceValidationError(
            "Total mismatch",
            "TOTAL_MISMATCH",
        )


def _sum_money(values: Iterable[Money]) -> Money:
    values = list(values)

    if not values:
        raise InvoiceValidationError(
            "Cannot sum empty money list",
            "INTERNAL_ERROR",
        )

    result = values[0]
    for value in values[1:]:
        result = result + value

    return result