from decimal import Decimal
from tax_engine.domain.money import Money
from tax_engine.domain.vat import VAT


class VATService:
    def __init__(self, rate: Decimal):
        self.vat = VAT(rate)

    def compute(self, net_amount: Money) -> Money:
        return self.vat.apply(net_amount)

    def gross_from_net(self, net_amount: Money) -> Money:
        return self.vat.gross_from_net(net_amount)