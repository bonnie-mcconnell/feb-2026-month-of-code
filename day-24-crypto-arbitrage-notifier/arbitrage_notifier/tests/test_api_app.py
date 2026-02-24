import pytest
from fastapi.testclient import TestClient
from arbitrage_notifier.api.app import app

client = TestClient(app)

def test_health_ok(monkeypatch):
    monkeypatch.setattr("arbitrage_notifier.api.app.cache.ping", lambda: True)
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()

def test_readiness(monkeypatch):
    from types import SimpleNamespace
    # simulate background task running
    monkeypatch.setattr("arbitrage_notifier.api.app.background_task", SimpleNamespace(done=lambda: False))
    r = client.get("/ready")
    assert r.json()["status"] == "ready"

def test_get_spread(monkeypatch):
    async def dummy_get(key):
        return "0.01"

    monkeypatch.setattr("arbitrage_notifier.api.app.cache.get", dummy_get)
    r = client.get("/spread")
    assert r.json()["spread"] == "0.01"

def test_metrics(monkeypatch):
    from prometheus_client import Counter
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.headers["content-type"] == "text/plain; charset=utf-8" or "text/plain"