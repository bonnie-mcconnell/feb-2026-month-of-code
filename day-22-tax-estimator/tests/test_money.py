from decimal import Decimal
import pytest

from src.tax_engine.domain.money import Money


# -----------------------------
# Construction
# -----------------------------

def test_construct_from_str_valid():
    m = Money.from_str("123.45", scale=2, rounding="ROUND_HALF_UP")
    assert m.to_decimal() == Decimal("123.45")


def test_construct_from_int_valid():
    m = Money.from_int(100, scale=2, rounding="ROUND_HALF_UP")
    assert m.to_decimal() == Decimal("100.00")


def test_reject_float_input():
    with pytest.raises(TypeError):
        Money.from_str(123.45, scale=2, rounding="ROUND_HALF_UP")  # type: ignore


def test_invalid_rounding_mode():
    with pytest.raises(ValueError):
        Money.from_str("10.00", scale=2, rounding="INVALID")


def test_invalid_string_value():
    with pytest.raises(ValueError):
        Money.from_str("abc", scale=2, rounding="ROUND_HALF_UP")


# -----------------------------
# Arithmetic
# -----------------------------

def test_addition():
    a = Money.from_str("10.00", scale=2, rounding="ROUND_HALF_UP")
    b = Money.from_str("5.00", scale=2, rounding="ROUND_HALF_UP")
    result = a.add(b)
    assert result.to_decimal() == Decimal("15.00")


def test_subtraction():
    a = Money.from_str("10.00", scale=2, rounding="ROUND_HALF_UP")
    b = Money.from_str("3.00", scale=2, rounding="ROUND_HALF_UP")
    result = a.subtract(b)
    assert result.to_decimal() == Decimal("7.00")


def test_multiplication():
    m = Money.from_str("100.00", scale=2, rounding="ROUND_HALF_UP")
    result = m.multiply(Decimal("0.153"))
    assert result.to_decimal() == Decimal("15.30")


def test_scale_mismatch_rejected():
    a = Money.from_str("10.00", scale=2, rounding="ROUND_HALF_UP")
    b = Money.from_str("5.000", scale=3, rounding="ROUND_HALF_UP")

    with pytest.raises(ValueError):
        a.add(b)


def test_rounding_policy_mismatch_rejected():
    a = Money.from_str("10.00", scale=2, rounding="ROUND_HALF_UP")
    b = Money.from_str("5.00", scale=2, rounding="ROUND_HALF_EVEN")

    with pytest.raises(ValueError):
        a.add(b)


# -----------------------------
# Rounding Edge Cases
# -----------------------------

def test_round_half_up_boundary():
    m = Money.from_str("0.005", scale=2, rounding="ROUND_HALF_UP")
    assert m.to_decimal() == Decimal("0.01")


def test_round_half_even_boundary():
    m = Money.from_str("0.005", scale=2, rounding="ROUND_HALF_EVEN")
    assert m.to_decimal() == Decimal("0.00")


def test_high_precision_input():
    m = Money.from_str("123.456789", scale=2, rounding="ROUND_HALF_UP")
    assert m.to_decimal() == Decimal("123.46")


def test_large_value():
    m = Money.from_str("1000000000000.99", scale=2, rounding="ROUND_HALF_UP")
    assert m.to_decimal() == Decimal("1000000000000.99")


# -----------------------------
# Negative Handling
# -----------------------------

def test_negative_value_allowed():
    m = Money.from_str("-10.00", scale=2, rounding="ROUND_HALF_UP")
    assert m.is_negative()


def test_zero_detection():
    m = Money.from_str("0.00", scale=2, rounding="ROUND_HALF_UP")
    assert m.is_zero()


# -----------------------------
# Determinism
# -----------------------------

def test_deterministic_operations():
    a = Money.from_str("123.45", scale=2, rounding="ROUND_HALF_UP")
    b = Money.from_str("67.89", scale=2, rounding="ROUND_HALF_UP")

    result1 = a.add(b)
    result2 = a.add(b)

    assert result1.to_decimal() == result2.to_decimal()