from decimal import Decimal
from pathlib import Path

from src.engine import FinanceEngine


def test_full_pipeline(tmp_path: Path):
    # Create sample transactions file
    tx_file = tmp_path / "tx.csv"
    tx_file.write_text(
        "date,description,amount\n"
        "2024-01-01,Starbucks,-5.00\n"
        "2024-01-02,Salary,2000.00\n"
        "2024-02-01,Starbucks,-1500.00\n"
    )

    # Create categories config
    config_file = tmp_path / "categories.json"
    config_file.write_text(
        """
        {
            "default_category": "Uncategorized",
            "rules": [
                {
                    "category": "Food",
                    "keywords": ["starbucks"]
                }
            ]
        }
        """
    )

    engine = FinanceEngine(config_file)
    result = engine.analyze(tx_file)

    # Categorization worked
    expenses = [t for t in result.transactions if t.is_expense]
    assert all(t.category == "Food" for t in expenses)

    # Aggregation worked
    assert result.report.total_income == Decimal("2000.00")

    # Anomaly detected for large transaction
    assert any(a.type == "large_transaction" for a in result.anomalies)
