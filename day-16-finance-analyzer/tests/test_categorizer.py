from decimal import Decimal
from datetime import date

from src.models import Transaction
from src.categorizer import Categorizer, CategoryRule


def build_categorizer():
    rules = [
        CategoryRule("Food", ["starbucks"]),
        CategoryRule("Transport", ["uber"]),
    ]
    return Categorizer(rules=rules, default_category="Uncategorized")


def test_keyword_match():
    tx = Transaction(date(2024, 1, 1), "Starbucks Coffee", Decimal("-5.00"))
    categorizer = build_categorizer()

    categorizer.categorize([tx])

    assert tx.category == "Food"


def test_priority_first_match_wins():
    tx = Transaction(date(2024, 1, 1), "Uber Starbucks", Decimal("-10.00"))
    rules = [
        CategoryRule("Food", ["starbucks"]),
        CategoryRule("Transport", ["uber"]),
    ]
    categorizer = Categorizer(rules, "Uncategorized")

    categorizer.categorize([tx])

    # Starbucks rule appears first
    assert tx.category == "Food"


def test_fallback_category():
    tx = Transaction(date(2024, 1, 1), "Unknown Merchant", Decimal("-5.00"))
    categorizer = build_categorizer()

    categorizer.categorize([tx])

    assert tx.category == "Uncategorized"


def test_income_not_categorized():
    tx = Transaction(date(2024, 1, 1), "Salary", Decimal("2000.00"))
    categorizer = build_categorizer()

    categorizer.categorize([tx])

    assert tx.category is None
