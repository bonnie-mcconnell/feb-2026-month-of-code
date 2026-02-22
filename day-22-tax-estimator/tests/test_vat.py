from decimal import Decimal
from tax_engine.domain.money import Money
from tax_engine.services.vat_estimator import VATService


def test_vat_apply():
    service = VATService(Decimal("0.15"))

    net = Money.from_str("100", scale=2, rounding="ROUND_HALF_UP")
    vat = service.compute(net)

    assert vat.to_decimal() == Decimal("15.00")


def test_vat_gross():
    service = VATService(Decimal("0.10"))

    net = Money.from_str("100", scale=2, rounding="ROUND_HALF_UP")
    gross = service.gross_from_net(net)

    assert gross.to_decimal() == Decimal("110.00")