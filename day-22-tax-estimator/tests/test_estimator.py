import json
from pathlib import Path
from decimal import Decimal

from tax_engine.domain.money import Money
from tax_engine.domain.deduction import DeductionSet
from tax_engine.services.estimator import TaxEstimator


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


def test_zero_income_effective_rate():
    estimator = TaxEstimator(CONFIG)

    gross = Money.from_int(0, scale=2, rounding="ROUND_HALF_UP")

    deductions = DeductionSet(
        standard=None,
        itemized=None,
        business=gross,
    )

    result = estimator.estimate(
        gross_income=gross,
        deductions=deductions,
    )

    assert result.effective_rate == Decimal("0")


def test_self_employment_tax_path(tmp_path: Path):
    # load real config
    original_path = Path("config/jurisdictions/nz_self_employed.json")

    data = json.loads(original_path.read_text())

    # inject self employment rate
    data["self_employment_rate"] = "0.10"

    temp_config = tmp_path / "nz_temp.json"
    temp_config.write_text(json.dumps(data))

    estimator = TaxEstimator(temp_config)

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

    assert result.self_employment_tax is not None
    assert result.total_tax.to_decimal() > result.income_tax.to_decimal()