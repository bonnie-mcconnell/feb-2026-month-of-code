from __future__ import annotations

from .money import Money


class DeductionSet:
    """
    Represents deduction inputs.

    - Standard OR itemized (mutually exclusive)
    - Business expenses separate
    """

    def __init__(
        self,
        *,
        standard: Money | None,
        itemized: Money | None,
        business: Money,
    ) -> None:

        if standard and itemized:
            raise ValueError("Cannot apply both standard and itemized deductions")

        if business.is_negative():
            raise ValueError("Business deductions cannot be negative")

        if standard and standard.is_negative():
            raise ValueError("Standard deduction cannot be negative")

        if itemized and itemized.is_negative():
            raise ValueError("Itemized deduction cannot be negative")

        self._standard = standard
        self._itemized = itemized
        self._business = business

    # ---------------------------------

    def total(self, gross_income: Money) -> Money:
        """
        Returns total deduction capped at gross income.
        """

        if gross_income.is_negative():
            raise ValueError("Gross income cannot be negative")

        chosen = self._standard or self._itemized

        total = self._business

        if chosen:
            total = total.add(chosen)

        # Cap deduction at gross income
        if total.to_decimal() > gross_income.to_decimal():
            return gross_income

        return total