from decimal import Decimal
import pytest

from src.tax_engine.domain.money import Money
from src.tax_engine.domain.deduction import DeductionSet


def m(value: str) -> Money:
    return Money.from_str(value, scale=2, rounding="ROUND_HALF_UP")


# ----------------------------------------
# Validation
# ----------------------------------------

def test_reject_standard_and_itemized():
    with pytest.raises(ValueError):
        DeductionSet(
            standard=m("1000.00"),
            itemized=m("500.00"),
            business=m("200.00"),
        )


def test_reject_negative_business():
    with pytest.raises(ValueError):
        DeductionSet(
            standard=None,
            itemized=None,
            business=m("-100.00"),
        )


# ----------------------------------------
# Computation
# ----------------------------------------

def test_standard_only():
    ds = DeductionSet(
        standard=m("1000.00"),
        itemized=None,
        business=m("200.00"),
    )

    total = ds.total(m("5000.00"))
    assert total.to_decimal() == Decimal("1200.00")


def test_itemized_only():
    ds = DeductionSet(
        standard=None,
        itemized=m("800.00"),
        business=m("200.00"),
    )

    total = ds.total(m("5000.00"))
    assert total.to_decimal() == Decimal("1000.00")


def test_business_only():
    ds = DeductionSet(
        standard=None,
        itemized=None,
        business=m("300.00"),
    )

    total = ds.total(m("5000.00"))
    assert total.to_decimal() == Decimal("300.00")


def test_deduction_cannot_exceed_income():
    ds = DeductionSet(
        standard=m("10000.00"),
        itemized=None,
        business=m("5000.00"),
    )

    total = ds.total(m("8000.00"))
    assert total.to_decimal() == Decimal("8000.00")


def test_zero_income_results_zero_deduction():
    ds = DeductionSet(
        standard=m("1000.00"),
        itemized=None,
        business=m("200.00"),
    )

    total = ds.total(m("0.00"))
    assert total.to_decimal() == Decimal("0.00")


def test_reject_negative_gross_income():
    ds = DeductionSet(
        standard=m("1000.00"),
        itemized=None,
        business=m("200.00"),
    )

    with pytest.raises(ValueError):
        ds.total(m("-1.00"))


# ----------------------------------------
# Determinism
# ----------------------------------------

def test_deduction_deterministic():
    ds = DeductionSet(
        standard=m("1000.00"),
        itemized=None,
        business=m("200.00"),
    )

    g = m("5000.00")

    t1 = ds.total(g)
    t2 = ds.total(g)

    assert t1.to_decimal() == t2.to_decimal()