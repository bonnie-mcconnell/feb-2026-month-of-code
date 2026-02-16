from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from .database import SessionLocal
from .db_models import (
    transactions,
    monthly_summaries,
    category_spending,
    anomalies as anomalies_table,
)


class FinanceRepository:

    def __init__(self):
        self.session: Session = SessionLocal()

    def close(self):
        self.session.close()

    # ------------------------
    # Transaction persistence
    # ------------------------

    def save_transactions(self, tx_list):
        for tx in tx_list:
            stmt = insert(transactions).values(
                date=tx.date,
                description=tx.description,
                amount=tx.amount,
                category=tx.category,
                is_expense=tx.is_expense,
            )
            self.session.execute(stmt)

        self.session.commit()

    # ------------------------
    # Monthly summaries
    # ------------------------

    def save_report(self, report):
        summary_ids = []

        for summary in report.monthly_summaries:
            result = self.session.execute(
                insert(monthly_summaries).values(
                    year=summary.year,
                    month=summary.month,
                    total_income=summary.total_income,
                    total_expense=summary.total_expense,
                )
            )

            inserted_pk = result.inserted_primary_key
            if not inserted_pk:
                raise RuntimeError("Failed to retrieve inserted primary key")

            summary_id = inserted_pk[0]
            summary_ids.append(summary_id)

            for category, amount in summary.spending_by_category.items():
                self.session.execute(
                    insert(category_spending).values(
                        summary_id=summary_id,
                        category=category,
                        amount=amount,
                    )
                )   

        self.session.commit()
        return summary_ids

    # ------------------------
    # Anomalies
    # ------------------------

    def save_anomalies(self, anomaly_list):
        for a in anomaly_list:
            self.session.execute(
                insert(anomalies_table).values(
                    type=a.type,
                    message=a.message,
                    year=a.year,
                    month=a.month,
                    amount=a.amount,
                    category=a.category,
                )
            )

        self.session.commit()

    # ------------------------
    # Read: Monthly reports
    # ------------------------

    def get_all_reports(self):
        result = self.session.execute(
            select(monthly_summaries)
        )
        return result.fetchall()


    def get_report_by_period(self, year: int, month: int):
        result = self.session.execute(
            select(monthly_summaries).where(
                (monthly_summaries.c.year == year) &
                (monthly_summaries.c.month == month)
            )
        )
        return result.fetchone()


    # ------------------------
    # Read: Anomalies
    # ------------------------

    def get_all_anomalies(self):
        result = self.session.execute(
            select(anomalies_table)
        )
        return result.fetchall()

