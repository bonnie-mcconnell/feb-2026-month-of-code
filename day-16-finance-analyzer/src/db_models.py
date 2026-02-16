from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Date,
    Boolean,
    Numeric,
    ForeignKey,
    DateTime,
)
from datetime import datetime

metadata = MetaData()

transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("date", Date, nullable=False),
    Column("description", String, nullable=False),
    Column("amount", Numeric(18, 2), nullable=False),
    Column("category", String, nullable=False),
    Column("is_expense", Boolean, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

monthly_summaries = Table(
    "monthly_summaries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("year", Integer, nullable=False),
    Column("month", Integer, nullable=False),
    Column("total_income", Numeric(18, 2), nullable=False),
    Column("total_expense", Numeric(18, 2), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

category_spending = Table(
    "category_spending",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("summary_id", Integer, ForeignKey("monthly_summaries.id")),
    Column("category", String, nullable=False),
    Column("amount", Numeric(18, 2), nullable=False),
)

anomalies = Table(
    "anomalies",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String, nullable=False),
    Column("message", String, nullable=False),
    Column("year", Integer, nullable=False),
    Column("month", Integer, nullable=False),
    Column("amount", Numeric(18, 2), nullable=False),
    Column("category", String, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)
