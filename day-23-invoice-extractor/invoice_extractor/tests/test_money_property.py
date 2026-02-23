from hypothesis import given
from hypothesis.strategies import decimals
from decimal import Decimal

from invoice_extractor.domain.money import Money


@given(
    decimals(min_value=0, max_value=100000, places=2),
    decimals(min_value=0, max_value=100000, places=2),
)
def test_money_addition_commutative(a: Decimal, b: Decimal):
    m1 = Money(a, "USD")
    m2 = Money(b, "USD")

    assert m1 + m2 == m2 + m1


@given(decimals(min_value=0, max_value=100000, places=2))
def test_money_non_negative(a: Decimal):
    m = Money(a, "USD")
    assert not m.is_negative()