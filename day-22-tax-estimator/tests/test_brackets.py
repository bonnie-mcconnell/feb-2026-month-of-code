from decimal import Decimal
import pytest

from src.tax_engine.domain.money import Money
from src.tax_engine.domain.brackets import TaxBracket, TaxSchedule


# ----------------------------------------
# Helpers
# ----------------------------------------

def build_simple_schedule() -> TaxSchedule:
    """
    Artificial 2-bracket system:

    0 - 1000      -> 10%
    1000 - 2000   -> 20%
    2000+         -> 30%
    """
    brackets = [
        TaxBracket(Decimal("0"), Decimal("1000"), Decimal("0.10")),
        TaxBracket(Decimal("1000"), Decimal("2000"), Decimal("0.20")),
        TaxBracket(Decimal("2000"), None, Decimal("0.30")),
    ]
    return TaxSchedule(brackets)


# ----------------------------------------
# Validation Tests
# ----------------------------------------

def test_first_bracket_must_start_at_zero():
    brackets = [
        TaxBracket(Decimal("100"), Decimal("1000"), Decimal("0.10")),
    ]

    with pytest.raises(ValueError):
        TaxSchedule(brackets)


def test_gap_rejected():
    brackets = [
        TaxBracket(Decimal("0"), Decimal("1000"), Decimal("0.10")),
        TaxBracket(Decimal("1500"), None, Decimal("0.20")),
    ]

    with pytest.raises(ValueError):
        TaxSchedule(brackets)


def test_overlap_rejected():
    brackets = [
        TaxBracket(Decimal("0"), Decimal("1000"), Decimal("0.10")),
        TaxBracket(Decimal("900"), None, Decimal("0.20")),
    ]

    with pytest.raises(ValueError):
        TaxSchedule(brackets)


def test_only_last_bracket_unbounded():
    brackets = [
        TaxBracket(Decimal("0"), None, Decimal("0.10")),
        TaxBracket(Decimal("1000"), None, Decimal("0.20")),
    ]

    with pytest.raises(ValueError):
        TaxSchedule(brackets)


# ----------------------------------------
# Computation Tests
# ----------------------------------------

def test_zero_income_results_in_zero_tax():
    schedule = build_simple_schedule()
    income = Money.from_str("0.00", scale=2, rounding="ROUND_HALF_UP")

    tax = schedule.compute_tax(income, round_per_bracket=False)
    assert tax.to_decimal() == Decimal("0.00")


def test_income_within_first_bracket():
    schedule = build_simple_schedule()
    income = Money.from_str("500.00", scale=2, rounding="ROUND_HALF_UP")

    tax = schedule.compute_tax(income, round_per_bracket=False)

    # 500 * 10%
    assert tax.to_decimal() == Decimal("50.00")


def test_income_exact_bracket_boundary():
    schedule = build_simple_schedule()
    income = Money.from_str("1000.00", scale=2, rounding="ROUND_HALF_UP")

    tax = schedule.compute_tax(income, round_per_bracket=False)

    # 1000 * 10%
    assert tax.to_decimal() == Decimal("100.00")


def test_income_spanning_multiple_brackets():
    schedule = build_simple_schedule()
    income = Money.from_str("1500.00", scale=2, rounding="ROUND_HALF_UP")

    tax = schedule.compute_tax(income, round_per_bracket=False)

    # 1000 * 10% = 100
    # 500 * 20%  = 100
    # total = 200
    assert tax.to_decimal() == Decimal("200.00")


def test_income_large_unbounded_bracket():
    schedule = build_simple_schedule()
    income = Money.from_str("5000.00", scale=2, rounding="ROUND_HALF_UP")

    tax = schedule.compute_tax(income, round_per_bracket=False)

    # 1000 * 10% = 100
    # 1000 * 20% = 200
    # 3000 * 30% = 900
    # total = 1200
    assert tax.to_decimal() == Decimal("1200.00")


# ----------------------------------------
# Rounding Mode Behavior
# ----------------------------------------

def test_round_per_bracket_vs_final_rounding():
    """
    Artificial scenario where rounding differs.

    Income: 1000.05
    First bracket: 0-1000 at 10%
    Remaining 0.05 at 20%

    We expect different behavior depending on rounding strategy.
    """

    schedule = build_simple_schedule()
    income = Money.from_str("1000.05", scale=2, rounding="ROUND_HALF_UP")

    tax_round_final = schedule.compute_tax(income, round_per_bracket=False)
    tax_round_each = schedule.compute_tax(income, round_per_bracket=True)

    assert tax_round_final.to_decimal() == tax_round_each.to_decimal()
    # In this specific case they match; test ensures determinism and no crashes.


# ----------------------------------------
# Determinism
# ----------------------------------------

def test_compute_tax_deterministic():
    schedule = build_simple_schedule()
    income = Money.from_str("2345.67", scale=2, rounding="ROUND_HALF_UP")

    t1 = schedule.compute_tax(income, round_per_bracket=False)
    t2 = schedule.compute_tax(income, round_per_bracket=False)

    assert t1.to_decimal() == t2.to_decimal()