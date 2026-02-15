from decimal import Decimal
from pathlib import Path
import pytest

from src.loader import load_transactions


def test_load_valid_csv(tmp_path: Path):
    file = tmp_path / "tx.csv"
    file.write_text(
        "date,description,amount\n"
        "2024-01-01,Test,-10.50\n"
    )

    transactions = load_transactions(file)

    assert len(transactions) == 1
    tx = transactions[0]
    assert tx.description == "Test"
    assert tx.amount == Decimal("-10.50")
    assert tx.is_expense


def test_invalid_date(tmp_path: Path):
    file = tmp_path / "tx.csv"
    file.write_text(
        "date,description,amount\n"
        "bad-date,Test,-10.50\n"
    )

    with pytest.raises(ValueError):
        load_transactions(file)


def test_invalid_amount(tmp_path: Path):
    file = tmp_path / "tx.csv"
    file.write_text(
        "date,description,amount\n"
        "2024-01-01,Test,not-a-number\n"
    )

    with pytest.raises(ValueError):
        load_transactions(file)


def test_missing_fields(tmp_path: Path):
    file = tmp_path / "tx.csv"
    file.write_text(
        "date,description\n"
        "2024-01-01,Test\n"
    )

    with pytest.raises(ValueError):
        load_transactions(file)
