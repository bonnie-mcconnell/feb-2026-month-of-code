from decimal import Decimal
from datetime import date

from src.models import Transaction
from src.aggregator import build_spending_report


def build_transactions():
    return [
        Transaction(date(2024, 1, 1), "Salary", Decimal("2000.00")),
        Transaction(date(2024, 1, 2), "Starbucks", Decimal("-5.00"), category="Food"),
        Transaction(date(2024, 1, 3), "Amazon", Decimal("-20.00"), category="Shopping"),
        Transaction(date(2024, 2, 1), "Salary", Decimal("2000.00")),
        Transaction(date(2024, 2, 5), "Uber", Decimal("-50.00"), category="Transport"),
    ]


def test_global_totals():
    report = build_spending_report(build_transactions())

    assert report.total_income == Decimal("4000.00")
    assert report.total_expense == Decimal("75.00")
    assert report.net_balance == Decimal("3925.00")


def test_monthly_breakdown():
    report = build_spending_report(build_transactions())

    january = report.monthly_summaries[0]
    february = report.monthly_summaries[1]

    assert january.total_income == Decimal("2000.00")
    assert january.total_expense == Decimal("25.00")

    assert february.total_expense == Decimal("50.00")


def test_category_aggregation():
    report = build_spending_report(build_transactions())

    assert report.top_categories["Transport"] == Decimal("50.00")
    assert report.top_categories["Shopping"] == Decimal("20.00")
    assert report.top_categories["Food"] == Decimal("5.00")
