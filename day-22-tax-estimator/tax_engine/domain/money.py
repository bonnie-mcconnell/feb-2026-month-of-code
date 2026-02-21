from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from typing import Final


_ALLOWED_ROUNDING: Final = {
    "ROUND_HALF_UP": ROUND_HALF_UP,
    "ROUND_HALF_EVEN": ROUND_HALF_EVEN,
}


@dataclass(frozen=True)
class Money:
    """
    Immutable monetary value with explicit scale and rounding policy.

    - Uses Decimal internally
    - Enforces scale
    - Disallows float input
    - Deterministic arithmetic
    """

    _amount: Decimal
    scale: int
    rounding: str

    def __post_init__(self) -> None:
        if self.rounding not in _ALLOWED_ROUNDING:
            raise ValueError(f"Unsupported rounding mode: {self.rounding}")

        if not isinstance(self._amount, Decimal):
            raise TypeError("Money amount must be Decimal")

        if self.scale < 0:
            raise ValueError("Scale must be non-negative")

        quantized = self._quantize(self._amount)

        object.__setattr__(self, "_amount", quantized)

    # ---------------------------
    # Constructors
    # ---------------------------

    @classmethod
    def from_str(cls, value: str, *, scale: int, rounding: str) -> "Money":
        if isinstance(value, float):
            raise TypeError("Float input is not allowed")

        try:
            dec = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(f"Invalid monetary value: {value}") from exc

        return cls(dec, scale=scale, rounding=rounding)

    @classmethod
    def from_int(cls, value: int, *, scale: int, rounding: str) -> "Money":
        if not isinstance(value, int):
            raise TypeError("from_int requires integer input")

        dec = Decimal(value)
        return cls(dec, scale=scale, rounding=rounding)

    # ---------------------------
    # Core arithmetic
    # ---------------------------

    def add(self, other: "Money") -> "Money":
        self._ensure_compatible(other)
        return Money(
            self._amount + other._amount,
            scale=self.scale,
            rounding=self.rounding,
        )

    def subtract(self, other: "Money") -> "Money":
        self._ensure_compatible(other)
        return Money(
            self._amount - other._amount,
            scale=self.scale,
            rounding=self.rounding,
        )

    def multiply(self, rate: Decimal) -> "Money":
        if not isinstance(rate, Decimal):
            raise TypeError("Rate must be Decimal")

        result = self._amount * rate
        return Money(result, scale=self.scale, rounding=self.rounding)

    # ---------------------------
    # Internal helpers
    # ---------------------------

    def _quantize(self, value: Decimal) -> Decimal:
        quant = Decimal("1").scaleb(-self.scale)
        return value.quantize(quant, rounding=_ALLOWED_ROUNDING[self.rounding])

    def _ensure_compatible(self, other: "Money") -> None:
        if self.scale != other.scale:
            raise ValueError("Scale mismatch")
        if self.rounding != other.rounding:
            raise ValueError("Rounding policy mismatch")

    # ---------------------------
    # Accessors
    # ---------------------------

    def to_decimal(self) -> Decimal:
        return self._amount

    def to_minor_units(self) -> int:
        """
        Returns integer representation (e.g., cents).
        """
        factor = Decimal(10) ** self.scale
        return int(self._amount * factor)

    def is_negative(self) -> bool:
        return self._amount < 0

    def is_zero(self) -> bool:
        return self._amount == 0

    def __repr__(self) -> str:
        return f"Money(amount={str(self._amount)}, scale={self.scale}, rounding='{self.rounding}')"