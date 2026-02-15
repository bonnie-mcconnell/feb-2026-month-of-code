from collections import defaultdict
from decimal import Decimal
from typing import List, Dict, Tuple

from .models import Transaction, MonthlySummary, SpendingReport


def build_spending_report(transactions: List[Transaction]) -> SpendingReport:
    total_income = Decimal("0")
    total_expense = Decimal("0")

    monthly_data: Dict[Tuple[int, int], Dict] = defaultdict(lambda: {
        "income": Decimal("0"),
        "expense": Decimal("0"),
        "categories": defaultdict(lambda: Decimal("0")),
    })

    category_totals: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    uncategorized_count = 0

    for tx in transactions:
        year = tx.date.year
        month = tx.date.month

        bucket = monthly_data[(year, month)]

        if tx.is_income:
            total_income += tx.amount
            bucket["income"] += tx.amount
        elif tx.is_expense:
            expense_amount = -tx.amount  # convert to positive

            total_expense += expense_amount
            bucket["expense"] += expense_amount

            category = tx.category or "Uncategorized"
            bucket["categories"][category] += expense_amount
            category_totals[category] += expense_amount

            if category == "Uncategorized":
                uncategorized_count += 1

    monthly_summaries: List[MonthlySummary] = []

    for (year, month), data in sorted(monthly_data.items()):
        income = data["income"]
        expense = data["expense"]
        net = income - expense

        monthly_summaries.append(
            MonthlySummary(
                year=year,
                month=month,
                total_income=income,
                total_expense=expense,
                net=net,
                spending_by_category=dict(data["categories"]),
            )
        )

    net_balance = total_income - total_expense

    return SpendingReport(
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        monthly_summaries=monthly_summaries,
        top_categories=dict(sorted(
            category_totals.items(),
            key=lambda item: item[1],
            reverse=True,
        )),
        uncategorized_count=uncategorized_count,
    )
