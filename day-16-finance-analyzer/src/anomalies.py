from decimal import Decimal, ROUND_HALF_UP
from typing import List

from .models import Transaction, SpendingReport, Anomaly


LARGE_TRANSACTION_THRESHOLD = Decimal("1000")
MONTHLY_INCREASE_THRESHOLD = Decimal("0.40")
CATEGORY_INCREASE_THRESHOLD = Decimal("0.50")


def detect_anomalies(
    transactions: List[Transaction],
    report: SpendingReport,
) -> List[Anomaly]:
    anomalies: List[Anomaly] = []

    anomalies.extend(_detect_large_transactions(transactions))
    anomalies.extend(_detect_monthly_spike(report))
    anomalies.extend(_detect_category_spike(report))

    return anomalies


def _detect_large_transactions(transactions: List[Transaction]) -> List[Anomaly]:
    results: List[Anomaly] = []

    for tx in transactions:
        if tx.is_expense and -tx.amount > LARGE_TRANSACTION_THRESHOLD:
            results.append(
                Anomaly(
                    type="large_transaction",
                    message=f"Large expense detected: {-tx.amount}",
                    year=tx.date.year,
                    month=tx.date.month,
                    amount=-tx.amount,
                )
            )

    return results


def _detect_monthly_spike(report: SpendingReport) -> List[Anomaly]:
    results: List[Anomaly] = []

    summaries = report.monthly_summaries

    for i in range(1, len(summaries)):
        prev = summaries[i - 1]
        curr = summaries[i]

        if prev.total_expense == 0:
            continue

        increase = (curr.total_expense - prev.total_expense) / prev.total_expense
        percentage = (increase * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)  # round to integer

        if increase > MONTHLY_INCREASE_THRESHOLD:
            results.append(
                Anomaly(
                    type="monthly_spike",
                    message=f"Monthly expenses increased by {percentage}% compared to previous month",
                    year=curr.year,
                    month=curr.month,
                    amount=curr.total_expense,
                )
            )

    return results


def _detect_category_spike(report: SpendingReport) -> List[Anomaly]:
    results: List[Anomaly] = []

    summaries = report.monthly_summaries

    for i in range(1, len(summaries)):
        prev = summaries[i - 1]
        curr = summaries[i]

        for category, curr_amount in curr.spending_by_category.items():
            prev_amount = prev.spending_by_category.get(category, Decimal("0"))

            if prev_amount == 0:
                continue

            increase = (curr_amount - prev_amount) / prev_amount
            percentage = (increase * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP
            )  


            if increase > CATEGORY_INCREASE_THRESHOLD:
                results.append(
                    Anomaly(
                        type="category_spike",
                        message=(
                            f"{category} spending increased by "
                            f"{percentage}% compared to previous month"
                        ),
                        year=curr.year,
                        month=curr.month,
                        category=category,
                        amount=curr_amount,
                    )
                )

    return results
