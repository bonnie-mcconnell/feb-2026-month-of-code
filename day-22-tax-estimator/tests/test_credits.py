from decimal import Decimal
from pathlib import Path

from tax_engine.domain.money import Money
from tax_engine.domain.credits import FlatCredit, TaxCredit
from tax_engine.services.estimator import TaxEstimator
from tax_engine.domain.deduction import DeductionSet


class LargeCredit(TaxCredit):
    def apply(self, tax_due: Money) -> Money:
        # attempt to wipe tax out
        return Money.from_int(0, scale=tax_due.scale, rounding=tax_due.rounding)


CONFIG_PATH = Path("config/jurisdictions/nz_self_employed.json")

def test_flat_credit_reduces_tax():
    config_dir = Path("config/jurisdictions")
    sample = next(config_dir.glob("*.json"))

    credit_amount = Money.from_str("1000", scale=2, rounding="ROUND_HALF_UP")
    credit = FlatCredit(credit_amount)

    estimator = TaxEstimator(sample, credits=[credit])

    gross = Money.from_str("100000", scale=2, rounding="ROUND_HALF_UP")

    deductions = DeductionSet(
        standard=None,
        itemized=None,
        business=Money.from_str("0", scale=2, rounding="ROUND_HALF_UP"),
    )

    result = estimator.estimate(gross_income=gross, deductions=deductions)

    assert result.total_tax.to_decimal() >= Decimal("0")


def test_credit_caps_at_zero():
    estimator = TaxEstimator(CONFIG_PATH, credits=[LargeCredit()])

    gross = Money.from_str("1000", scale=2, rounding="ROUND_HALF_UP")

    deductions = DeductionSet(
        standard=None,
        itemized=None,
        business=Money.from_str("0", scale=2, rounding="ROUND_HALF_UP"),
    )

    result = estimator.estimate(
        gross_income=gross,
        deductions=deductions,
    )

    assert result.total_tax.to_decimal() == 0