from decimal import Decimal, getcontext
from typing import Union

getcontext().prec = 28


class Money:
    __slots__ = ("_amount",)

    def __init__(self, amount: Decimal):
        if not isinstance(amount, Decimal):
            raise TypeError("Money requires Decimal")
        self._amount = amount

    @property
    def amount(self) -> Decimal:
        return self._amount

    def __add__(self, other: "Money") -> "Money":
        self._validate(other)
        return Money(self._amount + other._amount)

    def __sub__(self, other: "Money") -> "Money":
        self._validate(other)
        return Money(self._amount - other._amount)

    def __mul__(self, multiplier: Decimal) -> "Money":
        if not isinstance(multiplier, Decimal):
            raise TypeError("Multiplier must be Decimal")
        return Money(self._amount * multiplier)

    def __truediv__(self, divisor: Decimal) -> "Money":
        if not isinstance(divisor, Decimal):
            raise TypeError("Divisor must be Decimal")
        return Money(self._amount / divisor)

    def __lt__(self, other: "Money") -> bool:
        self._validate(other)
        return self._amount < other._amount

    def __le__(self, other: "Money") -> bool:
        self._validate(other)
        return self._amount <= other._amount

    def __gt__(self, other: "Money") -> bool:
        self._validate(other)
        return self._amount > other._amount

    def __ge__(self, other: "Money") -> bool:
        self._validate(other)
        return self._amount >= other._amount

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount

    def __repr__(self) -> str:
        return f"Money({self._amount})"

    @staticmethod
    def _validate(other: "Money") -> None:
        if not isinstance(other, Money):
            raise TypeError("Operation requires Money instance")