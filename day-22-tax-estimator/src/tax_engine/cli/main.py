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

    parser.add_argument("--jurisdiction", required=True)
    parser.add_argument("--income")
    parser.add_argument("--standard-deduction")
    parser.add_argument("--itemized-deduction")
    parser.add_argument("--business-expenses", default="0")

    parser.add_argument(
        "--simulate",
        nargs=3,
        metavar=("START", "END", "STEP"),
        help="Simulate effective rate curve.",
    )

    parser.add_argument(
        "--year",
        help="Tax year version (e.g. 2024)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    file_name = args.jurisdiction
    if args.year:
        file_name = f"{file_name}_{args.year}"

    config_path = CONFIG_DIR / f"{file_name}.json"

    jurisdiction = Jurisdiction.load_from_file(config_path)
    estimator = TaxEstimator(config_path)

    if args.simulate:
        start, end, step = args.simulate

        start = int(start)
        end = int(end)
        step = int(step)

        print("Income,EffectiveRate")

        for income_value in range(start, end + 1, step):
            gross = Money.from_str(
                str(income_value),
                scale=jurisdiction.scale,
                rounding=jurisdiction.rounding,
            )

            deductions = DeductionSet(
                standard=None,
                itemized=None,
                business=Money.from_str("0", scale=jurisdiction.scale, rounding=jurisdiction.rounding),
            )

            result = estimator.estimate(gross_income=gross, deductions=deductions)

            print(f"{income_value},{result.effective_rate:.6f}")

        return

    if not args.income:
        parser.error("Must provide --income or use --simulate.")

    gross = Money.from_str(
        args.income,
        scale=jurisdiction.scale,
        rounding=jurisdiction.rounding,
    )

    deductions = DeductionSet(
        standard=None,
        itemized=None,
        business=Money.from_str(
            args.business_expenses,
            scale=jurisdiction.scale,
            rounding=jurisdiction.rounding,
        ),
    )

    result = estimator.estimate(gross_income=gross, deductions=deductions)

    print("\n--- Tax Estimation Result ---")
    print(f"Jurisdiction: {jurisdiction.name}")
    print(f"Gross income: {gross.to_decimal()}")
    print(f"Total deductions: {deductions.total(gross).to_decimal()}")
    print(f"Taxable income: {result.taxable_income.to_decimal()}")
    print(f"Income tax: {result.income_tax.to_decimal()}")

    if result.self_employment_tax is not None:
        print(f"Self-employment tax: {result.self_employment_tax.to_decimal()}")
    else:
        print("Self-employment tax: 0.00")

    print(f"Total tax: {result.total_tax.to_decimal()}")
    print(f"Effective rate: {result.effective_rate:.6f}")

if __name__ == "__main__":
    main()