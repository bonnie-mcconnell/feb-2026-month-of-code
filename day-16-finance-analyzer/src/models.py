from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional, Dict, List


@dataclass
class Transaction:
    date: date
    description: str
    amount: Decimal
    category: Optional[str] = None

    @property
    def is_expense(self) -> bool:
        return self.amount < 0

    @property
    def is_income(self) -> bool:
        return self.amount > 0


@dataclass
class MonthlySummary:
    year: int
    month: int
    total_income: Decimal
    total_expense: Decimal
    net: Decimal
    spending_by_category: Dict[str, Decimal] = field(default_factory=dict)


@dataclass
class SpendingReport:
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    monthly_summaries: List[MonthlySummary]
    top_categories: Dict[str, Decimal]
    uncategorized_count: int


@dataclass
class Anomaly:
    type: str
    message: str
    year: int | None = None
    month: int | None = None
    category: str | None = None
    amount: Decimal | None = None


@dataclass
class AnalysisResult:
    transactions: List[Transaction]
    report: SpendingReport
    anomalies: List[Anomaly]