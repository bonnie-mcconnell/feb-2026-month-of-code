from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest
from pathlib import Path

from arbitrage_notifier.main import run_once, load_config, configure_logging

app = FastAPI(title="Crypto Arbitrage Notifier")

configure_logging()

config = load_config(Path("config/settings.json"))

REQUEST_COUNT = Counter(
    "arbitrage_runs_total",
    "Number of arbitrage executions"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run")
def run_arbitrage():
    REQUEST_COUNT.inc()
    run_once(config)
    return {"status": "executed"}


@app.get("/config")
def get_config():
    return config


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")