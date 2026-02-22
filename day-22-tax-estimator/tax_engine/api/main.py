from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path

from tax_engine.domain.money import Money
from tax_engine.domain.deduction import DeductionSet
from tax_engine.services.estimator import TaxEstimator

app = FastAPI()
CONFIG_DIR = Path("config/jurisdictions")


class EstimateRequest(BaseModel):
    jurisdiction: str
    income: str
    business_expenses: str = "0"


@app.post("/estimate")
def estimate(req: EstimateRequest):
    config = CONFIG_DIR / f"{req.jurisdiction}.json"
    estimator = TaxEstimator(config)

    gross = Money.from_str(req.income, scale=2, rounding="ROUND_HALF_UP")

    deductions = DeductionSet(
        standard=None,
        itemized=None,
        business=Money.from_str(req.business_expenses, scale=2, rounding="ROUND_HALF_UP"),
    )

    result = estimator.estimate(gross_income=gross, deductions=deductions)

    return {
        "taxable_income": str(result.taxable_income.to_decimal()),
        "total_tax": str(result.total_tax.to_decimal()),
        "effective_rate": str(result.effective_rate),
    }