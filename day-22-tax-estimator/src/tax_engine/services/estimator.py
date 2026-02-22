from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable

from tax_engine.domain.money import Money
from tax_engine.domain.jurisdiction import Jurisdiction
from tax_engine.domain.deduction import DeductionSet
from tax_engine.domain.credits import TaxCredit


@dataclass(frozen=True)
class EstimationResult:
    gross_income: Money
    taxable_income: Money
    total_deductions: Money
    income_tax: Money
    self_employment_tax: Money | None
    total_tax: Money
    effective_rate: Decimal


class TaxEstimator:
    def __init__(
        self,
        config_path: Path,
        credits: Iterable[TaxCredit] | None = None,
    ) -> None:
        self._config_path = config_path
        self._jurisdiction = Jurisdiction.load_from_file(config_path)
        self._credits = list(credits) if credits else []

    def estimate(
        self,
        *,
        gross_income: Money,
        deductions: DeductionSet,
    ) -> EstimationResult:

        jurisdiction = self._jurisdiction

        total_deductions = deductions.total(gross_income)

        taxable_income = gross_income.subtract(total_deductions)

        if taxable_income.is_negative():
            taxable_income = Money.from_int(
                0,
                scale=gross_income.scale,
                rounding=gross_income.rounding,
            )

        income_tax = jurisdiction.tax_schedule.compute_tax(
            taxable_income,
            round_per_bracket=jurisdiction.round_per_bracket,
        )

        self_employment_tax: Money | None = None
        total_tax = income_tax

        if jurisdiction.self_employment_rate:
            se_amount = taxable_income.multiply(jurisdiction.self_employment_rate)
            self_employment_tax = se_amount
            total_tax = total_tax.add(se_amount)

        # -------------------------
        # Apply tax credits
        # -------------------------
        for credit in self._credits:
            total_tax = credit.apply(total_tax)

        if gross_income.is_zero():
            effective_rate = Decimal("0")
        else:
            effective_rate = total_tax.to_decimal() / gross_income.to_decimal()

        return EstimationResult(
            gross_income=gross_income,
            taxable_income=taxable_income,
            total_deductions=total_deductions,
            income_tax=income_tax,
            self_employment_tax=self_employment_tax,
            total_tax=total_tax,
            effective_rate=effective_rate,
        )