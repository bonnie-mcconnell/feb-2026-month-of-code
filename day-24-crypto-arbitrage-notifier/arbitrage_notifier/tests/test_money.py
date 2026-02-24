import pytest
from decimal import Decimal
from arbitrage_notifier.domain.money import Money


def test_money_requires_decimal():
    with pytest.raises(TypeError):
        Money(100)  # type: ignore[arg-type]
        # int not allowed


def test_money_addition():
    a = Money(Decimal("10.5"))
    b = Money(Decimal("2.5"))
    result = a + b
    assert result.amount == Decimal("13.0")


def test_money_subtraction():
    a = Money(Decimal("10"))
    b = Money(Decimal("3"))
    result = a - b
    assert result.amount == Decimal("7")


def test_money_multiplication():
    a = Money(Decimal("100"))
    result = a * Decimal("1.01")
    assert result.amount == Decimal("101")


def test_money_comparison():
    a = Money(Decimal("5"))
    b = Money(Decimal("10"))
    assert a < b
    assert b > a
    assert a != b


def test_money_division():
    a = Money(Decimal("100"))
    result = a / Decimal("4")
    assert result.amount == Decimal("25")


def test_money_invalid_operations():
    a = Money(Decimal("10"))

    with pytest.raises(TypeError):
        a + 5  # type: ignore[operator]
        # invalid 

    with pytest.raises(TypeError):
        a * 2  # type:ignore[arg-type]
        # int not allowed 

def test_money_equality_false():
    a = Money(Decimal("10"))
    assert a != 10

