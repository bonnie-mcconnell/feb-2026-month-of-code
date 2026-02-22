from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from .money import Money


@dataclass(frozen=True)
class TaxBracket:
    minimum: Decimal
    maximum: Optional[Decimal]  # None = unbounded
    rate: Decimal

    def __post_init__(self) -> None:
        if self.minimum < Decimal("0"):
            raise ValueError("Bracket minimum must be >= 0")

        if self.maximum is not None and self.maximum <= self.minimum:
            raise ValueError("Bracket maximum must be greater than minimum")

        if not (Decimal("0") <= self.rate <= Decimal("1")):
            raise ValueError("Tax rate must be between 0 and 1")


class TaxSchedule:
    def __init__(self, brackets: List[TaxBracket]) -> None:
        if not brackets:
            raise ValueError("Tax schedule must contain at least one bracket")

        self._brackets = sorted(brackets, key=lambda b: b.minimum)
        self._validate_continuity()

    # ----------------------------
    # Validation
    # ----------------------------

    def _validate_continuity(self) -> None:
        first = self._brackets[0]
        if first.minimum != Decimal("0"):
            raise ValueError("First bracket must start at 0")

        for i in range(len(self._brackets) - 1):
            current = self._brackets[i]
            nxt = self._brackets[i + 1]

            if current.maximum is None:
                raise ValueError("Only final bracket may be unbounded")

            if current.maximum != nxt.minimum:
                raise ValueError("Brackets must be continuous without gaps or overlaps")

        # Ensure only final bracket is unbounded
        for b in self._brackets[:-1]:
            if b.maximum is None:
                raise ValueError("Only last bracket may have no maximum")

    # ----------------------------
    # Computation
    # ----------------------------

    def compute_tax(
        self,
        taxable_income: Money,
        *,
        round_per_bracket: bool
    ) -> Money:

        remaining = taxable_income.to_decimal()
        total_tax = Decimal("0")

        for bracket in self._brackets:
            if remaining <= bracket.minimum:
                continue

            upper_bound = (
                bracket.maximum
                if bracket.maximum is not None
                else remaining
            )

            taxable_in_bracket = min(remaining, upper_bound) - bracket.minimum

            if taxable_in_bracket <= Decimal("0"):
                continue

            tax_for_bracket = taxable_in_bracket * bracket.rate

            if round_per_bracket:
                money_tax = Money(
                    tax_for_bracket,
                    scale=taxable_income.scale,
                    rounding=taxable_income.rounding,
                )
                total_tax += money_tax.to_decimal()
            else:
                total_tax += tax_for_bracket

        return Money(
            total_tax,
            scale=taxable_income.scale,
            rounding=taxable_income.rounding,
        )