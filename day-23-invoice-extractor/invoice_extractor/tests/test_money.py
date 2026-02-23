import pytest
from decimal import Decimal
from typing import cast

from invoice_extractor.domain.money import Money, CurrencyMismatchError


# -------------------------
# Construction & Rounding
# -------------------------

def test_money_quantizes_half_up():
    m1 = Money("10.005", "usd")
    m2 = Money("10.004", "usd")

    assert m1.amount == Decimal("10.01")
    assert m2.amount == Decimal("10.00")


def test_currency_normalized_to_uppercase():
    m = Money("5.00", "usd")
    assert m.currency == "USD"


def test_rejects_float_amount():
    with pytest.raises(TypeError):
        Money(cast(float, 10.5), "USD")


def test_rejects_invalid_amount_type():
    with pytest.raises(TypeError):
        Money(cast(object, object()), "USD")


def test_rejects_empty_currency():
    with pytest.raises(ValueError):
        Money("10.00", "")


# -------------------------
# Arithmetic
# -------------------------

def test_addition_same_currency():
    m1 = Money("10.00", "USD")
    m2 = Money("5.00", "USD")

    result = m1 + m2

    assert result.amount == Decimal("15.00")
    assert result.currency == "USD"


def test_subtraction_same_currency():
    m1 = Money("10.00", "USD")
    m2 = Money("3.25", "USD")

    result = m1 - m2

    assert result.amount == Decimal("6.75")


def test_multiplication_with_decimal():
    m = Money("10.00", "USD")
    result = m * Decimal("1.5")

    assert result.amount == Decimal("15.00")


def test_multiplication_with_int():
    m = Money("7.25", "USD")
    result = m * 2

    assert result.amount == Decimal("14.50")


def test_multiplication_rejects_float():
    m = Money("10.00", "USD")

    with pytest.raises(TypeError):
        m * cast(float, 1.5)


def test_currency_mismatch_addition():
    m1 = Money("10.00", "USD")
    m2 = Money("5.00", "EUR")

    with pytest.raises(CurrencyMismatchError):
        _ = m1 + m2


def test_currency_mismatch_subtraction():
    m1 = Money("10.00", "USD")
    m2 = Money("5.00", "EUR")

    with pytest.raises(CurrencyMismatchError):
        _ = m1 - m2


# -------------------------
# Deterministic Serialization
# -------------------------

def test_json_serialization_always_two_decimals():
    m = Money("10", "USD")
    assert m.to_json_value() == "10.00"

    m2 = Money("10.5", "USD")
    assert m2.to_json_value() == "10.50"


def test_negative_detection():
    m = Money("-5.00", "USD")
    assert m.is_negative() is True

    m2 = Money("0.00", "USD")
    assert m2.is_negative() is False


# -------------------------
# Equality
# -------------------------

def test_money_equality():
    m1 = Money("10.00", "USD")
    m2 = Money("10.00", "USD")
    m3 = Money("10.00", "EUR")

    assert m1 == m2
    assert m1 != m3