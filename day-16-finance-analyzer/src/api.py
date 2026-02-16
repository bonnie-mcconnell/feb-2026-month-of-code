from fastapi import FastAPI, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile
from pathlib import Path

from .engine import FinanceEngine
from .api_models import (
    AnalyzeResponseModel,
    SpendingReportModel,
    AnomalyModel,
)

app = FastAPI(
    title="Finance Analyzer API",
    version="0.1.0",
    description="Deterministic financial analytics engine with rule-based categorization and anomaly detection.",
)

DEFAULT_CONFIG_PATH = Path("config/categories.json")


def _process_file(file: UploadFile):
    try:
        with NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        return engine.analyze(tmp_path)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/analyze",
    response_model=AnalyzeResponseModel,
    summary="Run full analysis",
    description="Uploads a CSV file and returns full financial analysis including report and detected anomalies.",
)
def analyze(file: UploadFile = File(...)):
    result = _process_file(file)
    return {
        "report": result.report,
        "anomalies": result.anomalies,
    }


@app.post(
    "/report",
    response_model=SpendingReportModel,
    summary="Generate spending report",
    description="Uploads a CSV file and returns aggregated monthly spending report.",
)
def report(file: UploadFile = File(...)):
    result = _process_file(file)
    return result.report


@app.post(
    "/anomalies",
    response_model=list[AnomalyModel],
    summary="Detect anomalies",
    description="Uploads a CSV file and returns detected spending anomalies.",
)
def anomalies(file: UploadFile = File(...)):
    result = _process_file(file)
    return result.anomalies
