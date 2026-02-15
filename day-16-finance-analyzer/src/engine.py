from pathlib import Path
from typing import List

from .loader import load_transactions
from .categorizer import Categorizer
from .aggregator import build_spending_report
from .anomalies import detect_anomalies
from .models import AnalysisResult, Transaction


class FinanceEngine:
    def __init__(self, categories_config_path: str | Path):
        self.categories_config_path = Path(categories_config_path)

        if not self.categories_config_path.exists():
            raise FileNotFoundError(
                f"Categories config not found: {self.categories_config_path}"
            )

        self._categorizer = Categorizer.from_json(self.categories_config_path)

    def analyze(self, transactions_path: str | Path) -> AnalysisResult:
        transactions: List[Transaction] = load_transactions(transactions_path)

        # Categorize expenses
        self._categorizer.categorize(transactions)

        # Aggregate
        report = build_spending_report(transactions)

        # Detect anomalies
        anomalies = detect_anomalies(transactions, report)

        return AnalysisResult(
            transactions=transactions,
            report=report,
            anomalies=anomalies,
        )
