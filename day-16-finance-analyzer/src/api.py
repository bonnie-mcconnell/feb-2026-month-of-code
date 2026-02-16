from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from tempfile import NamedTemporaryFile
from pathlib import Path
from pydantic import BaseModel
import os

from .engine import FinanceEngine
from .api_models import (
    AnalyzeResponseModel,
    SpendingReportModel,
    AnomalyModel,
    PersistedReportModel,
    PersistedAnomalyModel,
)
from .repository import FinanceRepository


app = FastAPI(
    title="Finance Analyzer API",
    version="0.1.0",
    description="Deterministic financial analytics engine with rule-based categorization and anomaly detection.",
)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config" / "categories.json"


ANALYZE_EXAMPLE = {
    "report": {
        "monthly_summaries": [
            {
                "year": 2024,
                "month": 2,
                "total_income": "2500.00",
                "total_expense": "40.39",
                "spending_by_category": {
                    "Food & Drink": "5.40",
                    "Shopping": "34.99",
                },
            }
        ]
    },
    "anomalies": [
        {
            "type": "large_transaction",
            "message": "Large expense detected: 1200.00",
            "year": 2024,
            "month": 3,
            "amount": "1200.00",
            "category": None,
        }
    ],
}

REPORT_EXAMPLE = ANALYZE_EXAMPLE["report"]

ANOMALY_EXAMPLE = ANALYZE_EXAMPLE["anomalies"]


# -----------------------------
# Models
# -----------------------------
class IngestResponseModel(BaseModel):
    status: str
    transactions_processed: int
    reports_created: int
    anomalies_detected: int


# -----------------------------
# Utilities
# -----------------------------
def _save_upload_to_temp(file: UploadFile) -> str:
    with NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        return tmp.name


def get_repo():
    repo = FinanceRepository()
    try:
        yield repo
    finally:
        repo.close()


# -----------------------------
# POST: Analysis Endpoints
# -----------------------------
@app.post(
    "/analyze",
    tags=["Analysis"],
    response_model=AnalyzeResponseModel,
    summary="Run full analysis",
    description="Uploads a CSV file and returns full financial analysis including report and detected anomalies.",
    responses={
        200: {
            "description": "Successful analysis result",
            "content": {
                "application/json": {
                    "example": ANALYZE_EXAMPLE
                }
            },
        }
    },
)
def analyze(file: UploadFile = File(...)):
    tmp_path = _save_upload_to_temp(file)
    try:
        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        result = engine.analyze(tmp_path)
        return {"report": result.report, "anomalies": result.anomalies}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post(
    "/report",
    tags=["Analysis"],
    response_model=SpendingReportModel,
    summary="Generate spending report",
    description="Uploads a CSV file and returns aggregated monthly spending report.",
    responses={
        200: {
            "description": "Aggregated monthly spending report",
            "content": {
                "application/json": {
                    "example": REPORT_EXAMPLE
                }
            },
        }
    },
)
def report(file: UploadFile = File(...)):
    tmp_path = _save_upload_to_temp(file)
    try:
        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        result = engine.analyze(tmp_path)
        return result.report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post(
    "/anomalies",
    tags=["Analysis"],
    response_model=list[AnomalyModel],
    summary="Detect anomalies",
    description="Uploads a CSV file and returns detected spending anomalies.",
    responses={
        200: {
            "description": "Detected anomalies",
            "content": {
                "application/json": {
                    "example": ANOMALY_EXAMPLE
                }
            },
        }
    },
)
def anomalies(file: UploadFile = File(...)):
    tmp_path = _save_upload_to_temp(file)
    try:
        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        result = engine.analyze(tmp_path)
        return result.anomalies
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# -----------------------------
# POST: Persisted ingestion
# -----------------------------
@app.post(
    "/ingest", 
    tags=["Persistence"],
    response_model=IngestResponseModel, 
    responses={
        200: {
            "description": "Successful ingestion",
            "content": {
                "application/json": {
                    "example": {
                        "status": "persisted",
                        "transactions_processed": 6,
                        "reports_created": 2,
                        "anomalies_detected": 2
                    }
                }
            }
        }
    }
)
def ingest(file: UploadFile = File(...)):
    tmp_path = _save_upload_to_temp(file)
    try:
        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        result = engine.analyze(tmp_path, persist=True)
        return {
            "status": "persisted",
            "transactions_processed": len(result.transactions),
            "reports_created": len(result.report.monthly_summaries),
            "anomalies_detected": len(result.anomalies),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# -----------------------------
# GET: Reports
# -----------------------------
@app.get("/reports", tags=["Persistence"], response_model=list[PersistedReportModel])
def get_reports(repo: FinanceRepository = Depends(get_repo)):
    rows = repo.get_all_reports()
    result = []
    for row in rows:
        r = dict(row._mapping)
        r["total_income"] = str(r["total_income"])
        r["total_expense"] = str(r["total_expense"])
        result.append(r)
    return result


@app.get("/reports/{year}/{month}", tags=["Persistence"], response_model=PersistedReportModel)
def get_report(year: int, month: int, repo: FinanceRepository = Depends(get_repo)):
    row = repo.get_report_by_period(year, month)
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    r = dict(row._mapping)
    r["total_income"] = str(r["total_income"])
    r["total_expense"] = str(r["total_expense"])
    return r


# -----------------------------
# GET: Anomaly history
# -----------------------------
@app.get("/anomalies/history", tags=["Persistence"], response_model=list[PersistedAnomalyModel])
def get_anomalies_history(repo: FinanceRepository = Depends(get_repo)):
    rows = repo.get_all_anomalies()
    result = []
    for row in rows:
        r = dict(row._mapping)
        r["amount"] = str(r["amount"])
        result.append(r)
    return result


# -----------------------------
# GET: Health
# -----------------------------
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
