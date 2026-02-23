from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Union


TWOPLACES = Decimal("0.01")


SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
}


class CurrencyMismatchError(Exception):
    pass


class Money:
    """
    Deterministic money representation.
    - Backed by Decimal
    - Fixed 2 decimal quantization
    - Explicit ROUND_HALF_UP
    """

    __slots__ = ("_amount", "currency")

    def __init__(self, amount: Union[str, Decimal], currency: str) -> None:
        if isinstance(amount, float):
            raise TypeError("Money does not accept float values.")

        if isinstance(amount, str):
            amount = Decimal(amount)

        if not isinstance(amount, Decimal):
            raise TypeError("Amount must be Decimal or string.")

        if not currency or not isinstance(currency, str):
            raise ValueError("Currency must be a non-empty string.")

        self.currency = currency.upper()
        self._amount = self._quantize(amount)

    @staticmethod
    def _quantize(value: Decimal) -> Decimal:
        return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    @property
    def amount(self) -> Decimal:
        return self._amount

    def _assert_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                f"Currency mismatch: {self.currency} != {other.currency}"
            )

    def __add__(self, other: Money) -> Money:
        self._assert_same_currency(other)
        return Money(self._amount + other._amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._assert_same_currency(other)
        return Money(self._amount - other._amount, self.currency)

    def __mul__(self, multiplier: Union[int, Decimal]) -> Money:
        if isinstance(multiplier, float):
            raise TypeError("Multiplier cannot be float.")

        if isinstance(multiplier, int):
            multiplier = Decimal(multiplier)

        if not isinstance(multiplier, Decimal):
            raise TypeError("Multiplier must be int or Decimal.")

        result = self._amount * multiplier
        return Money(result, self.currency)

    def is_negative(self) -> bool:
        return self._amount < 0

    def to_json_value(self) -> str:
        """
        Serialize as string to preserve deterministic decimal representation.
        """
        return format(self._amount, ".2f")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.currency == other.currency and self._amount == other._amount

    def __repr__(self) -> str:
        return f"Money(amount={self._amount}, currency='{self.currency}')"
    
    @staticmethod
    def detect_currency(value: str) -> str:
        for symbol, code in SYMBOL_MAP.items():
            if symbol in value:
                return code
        return "USD"