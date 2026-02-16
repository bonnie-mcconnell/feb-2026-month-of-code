from fastapi import FastAPI, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile
from pathlib import Path

from .engine import FinanceEngine
from .api_models import (
    AnalyzeResponseModel,
    SpendingReportModel,
    AnomalyModel,
)
from .repository import FinanceRepository


app = FastAPI(
    title="Finance Analyzer API",
    version="0.1.0",
    description="Deterministic financial analytics engine with rule-based categorization and anomaly detection.",
)

DEFAULT_CONFIG_PATH = Path("config/categories.json")


def _save_upload_to_temp(file: UploadFile) -> str:
    with NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        return tmp.name


@app.post(
    "/analyze",
    response_model=AnalyzeResponseModel,
    summary="Run full analysis",
)
def analyze(file: UploadFile = File(...)):
    try:
        tmp_path = _save_upload_to_temp(file)
        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        result = engine.analyze(tmp_path)

        return {
            "report": result.report,
            "anomalies": result.anomalies,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/report",
    response_model=SpendingReportModel,
    summary="Generate spending report",
)
def report(file: UploadFile = File(...)):
    try:
        tmp_path = _save_upload_to_temp(file)
        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        result = engine.analyze(tmp_path)
        return result.report

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/anomalies",
    response_model=list[AnomalyModel],
    summary="Detect anomalies",
)
def anomalies(file: UploadFile = File(...)):
    try:
        tmp_path = _save_upload_to_temp(file)
        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        result = engine.analyze(tmp_path)
        return result.anomalies

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# NEW: Persisted ingestion
# -----------------------------

@app.post("/ingest")
def ingest(file: UploadFile = File(...)):
    try:
        tmp_path = _save_upload_to_temp(file)
        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        engine.analyze(tmp_path, persist=True)

        return {"status": "persisted"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# GET: Reports
# -----------------------------

@app.get("/reports")
def get_reports():
    repo = FinanceRepository()
    try:
        rows = repo.get_all_reports()
        return [dict(row._mapping) for row in rows]
    finally:
        repo.close()


@app.get("/reports/{year}/{month}")
def get_report(year: int, month: int):
    repo = FinanceRepository()
    try:
        row = repo.get_report_by_period(year, month)
        if not row:
            raise HTTPException(status_code=404, detail="Report not found")
        return dict(row._mapping)
    finally:
        repo.close()


# -----------------------------
# GET: Anomaly history
# -----------------------------

@app.get("/anomalies/history")
def get_anomalies_history():
    repo = FinanceRepository()
    try:
        rows = repo.get_all_anomalies()
        return [dict(row._mapping) for row in rows]
    finally:
        repo.close()
