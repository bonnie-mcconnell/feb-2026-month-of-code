from decimal import Decimal
from hypothesis import given, strategies as st

from tax_engine.domain.brackets import TaxBracket, TaxSchedule
from tax_engine.domain.money import Money


@given(
    income=st.decimals(min_value=0, max_value=1_000_000, places=2)
)
def test_tax_is_monotonic(income):
    brackets = [
        TaxBracket(Decimal("0"), Decimal("50000"), Decimal("0.1")),
        TaxBracket(Decimal("50000"), None, Decimal("0.2")),
    ]

    schedule = TaxSchedule(brackets)

    m = Money(income, scale=2, rounding="ROUND_HALF_UP")

    tax = schedule.compute_tax(m, round_per_bracket=False)

    assert tax.to_decimal() >= Decimal("0")