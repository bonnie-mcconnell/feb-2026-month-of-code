import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List

from .models import Transaction


REQUIRED_FIELDS = {"date", "description", "amount"}


def load_transactions(path: str | Path) -> List[Transaction]:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    transactions: List[Transaction] = []

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if not REQUIRED_FIELDS.issubset(reader.fieldnames or []):
            raise ValueError(
                f"CSV must contain fields: {', '.join(sorted(REQUIRED_FIELDS))}"
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                tx_date = datetime.fromisoformat(row["date"]).date()
            except Exception:
                raise ValueError(
                    f"Invalid date at row {row_number}: {row['date']}"
                )

            description = (row["description"] or "").strip()
            if not description:
                raise ValueError(f"Empty description at row {row_number}")

            try:
                amount = Decimal(row["amount"])
            except (InvalidOperation, TypeError):
                raise ValueError(
                    f"Invalid amount at row {row_number}: {row['amount']}"
                )

            transactions.append(
                Transaction(
                    date=tx_date,
                    description=description,
                    amount=amount,
                )
            )

    return transactions
