from pydantic import BaseModel
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import date, datetime


class TransactionModel(BaseModel):
    date: date
    description: str
    amount: Decimal
    category: str
    is_expense: bool

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class MonthlySummaryModel(BaseModel):
    year: int
    month: int
    total_income: Decimal
    total_expense: Decimal
    spending_by_category: Dict[str, Decimal]

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class SpendingReportModel(BaseModel):
    monthly_summaries: List[MonthlySummaryModel]

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class AnomalyModel(BaseModel):
    type: str
    message: str
    year: int
    month: int
    amount: Decimal
    category: Optional[str] = None

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class AnalyzeResponseModel(BaseModel):
    report: SpendingReportModel
    anomalies: List[AnomalyModel]

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class PersistedReportModel(BaseModel):
    year: int
    month: int
    total_income: str
    total_expense: str
    created_at: datetime

class PersistedAnomalyModel(BaseModel):
    type: str
    message: str
    year: int
    month: int
    amount: str
    category: Optional[str]
    created_at: datetime
