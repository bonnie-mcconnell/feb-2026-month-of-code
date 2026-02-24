import asyncio
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from arbitrage_notifier.api.app import spread_loop, cache, AlertEngine, ws_client, REQUEST_COUNT, app
from fastapi.testclient import TestClient

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


def test_health_endpoint(monkeypatch):
    monkeypatch.setattr("arbitrage_notifier.api.app.cache.ping", lambda: True)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ready_endpoint(monkeypatch):
    response = client.get("/ready")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_spread_loop_exceptions(monkeypatch):
    # Mock dependencies
    monkeypatch.setattr("arbitrage_notifier.api.app.BinanceClient", lambda limiter: MagicMock())
    monkeypatch.setattr("arbitrage_notifier.api.app.CoinbaseClient", lambda limiter: MagicMock(get_ticker=AsyncMock(side_effect=Exception("fail"))))
    monkeypatch.setattr("arbitrage_notifier.api.app.compute_best_spread", lambda **kwargs: None)
    monkeypatch.setattr("arbitrage_notifier.api.app.cache.set", AsyncMock())
    monkeypatch.setattr("arbitrage_notifier.api.app.AlertEngine.evaluate", lambda self, spread: None)
    
    # Run loop one iteration
    async def stop_loop_after_first():
        await asyncio.sleep(0.05)
        raise asyncio.CancelledError()
    
    task = asyncio.create_task(spread_loop())
    with pytest.raises(asyncio.CancelledError):
        await stop_loop_after_first()