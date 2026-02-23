from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from .line_item import LineItem
from .money import Money
from .validation import validate_invoice


@dataclass(slots=True)
class Vendor:
    name: str
    address: Optional[str] = None


@dataclass(slots=True)
class Customer:
    name: str


@dataclass(slots=True)
class Invoice:
    invoice_number: str
    invoice_date: date
    due_date: date
    vendor: Vendor
    customer: Customer
    currency: str
    line_items: List[LineItem]
    subtotal: Money
    tax: Money
    total: Money

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "vendor": {
                "name": self.vendor.name,
                "address": self.vendor.address,
            },
            "customer": {
                "name": self.customer.name,
            },
            "currency": self.currency,
            "line_items": [
                {
                    "description": li.description,
                    "quantity": int(li.quantity) if li.quantity == int(li.quantity) else float(li.quantity),
                    "unit_price": li.unit_price.to_json_value(),
                    "total": li.total.to_json_value(),
                }
                for li in self.line_items
            ],
            "subtotal": self.subtotal.to_json_value(),
            "tax": self.tax.to_json_value(),
            "total": self.total.to_json_value(),
        }

    
    @classmethod
    def create(
        cls,
        invoice_number: str,
        invoice_date: date,
        due_date: date,
        vendor: Vendor,
        customer: Customer,
        currency: str,
        line_items: list[LineItem],
        subtotal: Money,
        tax: Money,
        total: Money,
    ) -> Invoice:
        invoice = cls(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            vendor=vendor,
            customer=customer,
            currency=currency,
            line_items=line_items,
            subtotal=subtotal,
            tax=tax,
            total=total,
        )

        validate_invoice(invoice)

        return invoice

