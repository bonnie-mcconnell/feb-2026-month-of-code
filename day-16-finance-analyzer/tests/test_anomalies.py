from decimal import Decimal
from datetime import date

from src.models import Transaction
from src.aggregator import build_spending_report
from src.anomalies import detect_anomalies


def test_large_transaction_detected():
    txs = [
        Transaction(date(2024, 1, 1), "Big Purchase", Decimal("-1500.00")),
    ]

    report = build_spending_report(txs)
    anomalies = detect_anomalies(txs, report)

    assert any(a.type == "large_transaction" for a in anomalies)


def test_monthly_spike_detected():
    txs = [
        Transaction(date(2024, 1, 1), "Rent", Decimal("-1000.00"), category="Housing"),
        Transaction(date(2024, 2, 1), "Rent", Decimal("-2000.00"), category="Housing"),
    ]

    report = build_spending_report(txs)
    anomalies = detect_anomalies(txs, report)

    assert any(a.type == "monthly_spike" for a in anomalies)


def test_category_spike_detected():
    txs = [
        Transaction(date(2024, 1, 1), "Amazon", Decimal("-100.00"), category="Shopping"),
        Transaction(date(2024, 2, 1), "Amazon", Decimal("-300.00"), category="Shopping"),
    ]

    report = build_spending_report(txs)
    anomalies = detect_anomalies(txs, report)

    assert any(a.type == "category_spike" for a in anomalies)
