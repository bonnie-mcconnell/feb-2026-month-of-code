from pathlib import Path
from decimal import Decimal

from src.tax_engine.domain.money import Money
from src.tax_engine.domain.deduction import DeductionSet
from src.tax_engine.services.estimator import TaxEstimator


CONFIG = Path("config/jurisdictions/nz_self_employed.json")


def test_basic_estimation():
    estimator = TaxEstimator(CONFIG)

    gross = Money.from_str("100000", scale=2, rounding="ROUND_HALF_UP")

    deductions = DeductionSet(
        standard=None,
        itemized=None,
        business=Money.from_str("0", scale=2, rounding="ROUND_HALF_UP"),
    )

    result = estimator.estimate(
        gross_income=gross,
        deductions=deductions,
    )

    assert result.taxable_income.to_decimal() == Decimal("100000.00")
    assert result.total_tax.to_decimal() > Decimal("0")
    assert result.effective_rate > Decimal("0")