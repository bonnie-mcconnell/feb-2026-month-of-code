from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal

from tax_engine.domain.money import Money
from tax_engine.domain.deduction import DeductionSet
from tax_engine.domain.jurisdiction import Jurisdiction
from tax_engine.services.estimator import TaxEstimator


CONFIG_DIR = Path("config/jurisdictions")

app = FastAPI(
    title="Tax Engine API",
    description="Deterministic tax calculation engine using Decimal arithmetic.",
    version="1.0.0",
)


# ----------------------------
# Request/Response Schemas
# ----------------------------

class EstimateRequest(BaseModel):
    jurisdiction: str = Field(
        ...,
        json_schema_extra={"example": "nz_self_employed"},
    )
    income: str = Field(
        ...,
        json_schema_extra={"example": "100000"},
    )
    business_expenses: str = Field(
        default="0",
        json_schema_extra={"example": "5000"},
    )
    year: str | None = Field(
        default=None,
        json_schema_extra={"example": "2024"},
    )

class EstimateResponse(BaseModel):
    gross_income: str
    taxable_income: str
    income_tax: str
    self_employment_tax: str
    total_tax: str
    effective_rate: str

# ----------------------------
# Endpoint
# ----------------------------

@app.post("/estimate", response_model=EstimateResponse)
def estimate_tax(request: EstimateRequest) -> EstimateResponse:
    file_name = request.jurisdiction
    if request.year:
        file_name = f"{file_name}_{request.year}"

    config_path = CONFIG_DIR / f"{file_name}.json"

    if not config_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Jurisdiction config not found: {file_name}",
        )

    jurisdiction = Jurisdiction.load_from_file(config_path)
    estimator = TaxEstimator(config_path)

    gross = Money.from_str(
        request.income,
        scale=jurisdiction.scale,
        rounding=jurisdiction.rounding,
    )

    business = Money.from_str(
        request.business_expenses,
        scale=jurisdiction.scale,
        rounding=jurisdiction.rounding,
    )

    deductions = DeductionSet(
        standard=None,
        itemized=None,
        business=business,
    )

    result = estimator.estimate(gross_income=gross, deductions=deductions)

    return EstimateResponse(
        gross_income=str(gross.to_decimal()),
        taxable_income=str(result.taxable_income.to_decimal()),
        income_tax=str(result.income_tax.to_decimal()),
        self_employment_tax=str(result.self_employment_tax.to_decimal() if result.self_employment_tax else Decimal("0.00")),
        total_tax=str(result.total_tax.to_decimal()),
        effective_rate=f"{result.effective_rate:.6f}",
    )