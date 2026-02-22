from __future__ import annotations

import argparse
from pathlib import Path

from tax_engine.domain.money import Money
from tax_engine.domain.deduction import DeductionSet
from tax_engine.domain.jurisdiction import Jurisdiction
from tax_engine.services.estimator import TaxEstimator


CONFIG_DIR = Path("config/jurisdictions")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic tax estimator (Decimal-only engine)."
    )

    parser.add_argument(
        "--jurisdiction",
        required=True,
        help="Jurisdiction config file name (e.g. nz_self_employed)",
    )

    parser.add_argument(
        "--income",
        required=True,
        help="Gross income (string input, no floats)",
    )

    parser.add_argument("--standard-deduction")
    parser.add_argument("--itemized-deduction")
    parser.add_argument("--business-expenses", default="0")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config_path = CONFIG_DIR / f"{args.jurisdiction}.json"

    jurisdiction = Jurisdiction.load_from_file(config_path)

    gross = Money.from_str(
        args.income,
        scale=jurisdiction.scale,
        rounding=jurisdiction.rounding,
    )

    standard = (
        Money.from_str(
            args.standard_deduction,
            scale=jurisdiction.scale,
            rounding=jurisdiction.rounding,
        )
        if args.standard_deduction
        else None
    )

    itemized = (
        Money.from_str(
            args.itemized_deduction,
            scale=jurisdiction.scale,
            rounding=jurisdiction.rounding,
        )
        if args.itemized_deduction
        else None
    )

    business = Money.from_str(
        args.business_expenses,
        scale=jurisdiction.scale,
        rounding=jurisdiction.rounding,
    )

    deductions = DeductionSet(
        standard=standard,
        itemized=itemized,
        business=business,
    )

    estimator = TaxEstimator(config_path)

    result = estimator.estimate(
        gross_income=gross,
        deductions=deductions,
    )

    print("\n--- Tax Estimation Result ---")
    print(f"Jurisdiction: {jurisdiction.name}")
    print(f"Gross income: {result.gross_income.to_decimal()}")
    print(f"Total deductions: {result.total_deductions.to_decimal()}")
    print(f"Taxable income: {result.taxable_income.to_decimal()}")
    print(f"Income tax: {result.income_tax.to_decimal()}")

    if result.self_employment_tax:
        print(f"Self-employment tax: {result.self_employment_tax.to_decimal()}")

    print(f"Total tax: {result.total_tax.to_decimal()}")
    print(f"Effective rate: {result.effective_rate:.4f}")

if __name__ == "__main__":
    main()

# add to cli --simulate start end step
# Loop through range and print effective rate curve.