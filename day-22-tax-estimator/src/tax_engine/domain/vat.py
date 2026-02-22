from __future__ import annotations

from decimal import Decimal
from tax_engine.domain.money import Money


class VAT:
    def __init__(self, rate: Decimal) -> None:
        if not (Decimal("0") <= rate <= Decimal("1")):
            raise ValueError("VAT rate must be between 0 and 1")
        self.rate = rate

    def apply(self, net_amount: Money) -> Money:
        vat_amount = net_amount.multiply(self.rate)
        return vat_amount

    def gross_from_net(self, net_amount: Money) -> Money:
        return net_amount.add(self.apply(net_amount))