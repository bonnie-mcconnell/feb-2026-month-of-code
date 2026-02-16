from fastapi import FastAPI, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile
from pathlib import Path
from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from typing import Any
import json

from .engine import FinanceEngine

app = FastAPI(title="Finance Analyzer API")

DEFAULT_CONFIG_PATH = Path("config/categories.json")


def _serialize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj


def _process_file(file: UploadFile):
    try:
        with NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        engine = FinanceEngine(DEFAULT_CONFIG_PATH)
        result = engine.analyze(tmp_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze")
def analyze(file: UploadFile = File(...)):
    result = _process_file(file)
    return _serialize(asdict(result))


@app.post("/report")
def report(file: UploadFile = File(...)):
    result = _process_file(file)
    return _serialize(asdict(result.report))


@app.post("/anomalies")
def anomalies(file: UploadFile = File(...)):
    result = _process_file(file)
    return _serialize([asdict(a) for a in result.anomalies])
