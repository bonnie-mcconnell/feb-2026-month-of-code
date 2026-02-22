from dataclasses import dataclass
from pathlib import Path
from decimal import Decimal

from tax_engine.domain.money import Money
from tax_engine.domain.jurisdiction import Jurisdiction
from tax_engine.domain.deduction import DeductionSet


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

    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path

    def estimate(
        self,
        *,
        gross_income: Money,
        deductions: DeductionSet,
    ) -> EstimationResult:

        jurisdiction = Jurisdiction.load_from_file(self._config_path)

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

        self_employment_tax = None

        if jurisdiction.self_employment_rate:
            se_amount = taxable_income.multiply(jurisdiction.self_employment_rate)
            self_employment_tax = se_amount
            total_tax = income_tax.add(se_amount)
        else:
            total_tax = income_tax

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