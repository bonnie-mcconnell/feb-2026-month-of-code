import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from decimal import Decimal

from arbitrage_notifier.main import load_config, run_once_async, DEFAULT_CONFIG
from arbitrage_notifier.domain.money import Money
from arbitrage_notifier.domain.ticker import Ticker


def test_load_config_success():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        json.dump({"foo": "bar"}, f)
        path = Path(f.name)

    config = load_config(path)
    assert config["foo"] == "bar"


def test_load_config_missing():
    path = Path("nonexistent.json")

    with pytest.raises(FileNotFoundError):
        load_config(path)


@pytest.mark.asyncio
async def test_run_once_async_no_crash():
    config = DEFAULT_CONFIG.copy()

    binance_ticker = Ticker(
        exchange="binance",
        symbol="BTC",
        bid=Money(Decimal("100")),
        ask=Money(Decimal("101")),
        timestamp=datetime.now(timezone.utc),
    )

    coinbase_ticker = Ticker(
        exchange="coinbase",
        symbol="BTC",
        bid=Money(Decimal("102")),
        ask=Money(Decimal("103")),
        timestamp=datetime.now(timezone.utc),
    )

    with patch(
        "arbitrage_notifier.exchanges.binance_client.BinanceClient.get_ticker",
        new=AsyncMock(return_value=binance_ticker),
    ), patch(
        "arbitrage_notifier.exchanges.coinbase_client.CoinbaseClient.get_ticker",
        new=AsyncMock(return_value=coinbase_ticker),
    ):
        await run_once_async(config)


def test_load_config_file(tmp_path):
    path = tmp_path / "config.json"
    data = {"alert_threshold_percent": 0.05}
    path.write_text(json.dumps(data))
    cfg = load_config(path)
    assert cfg["alert_threshold_percent"] == 0.05


def test_load_config_env(monkeypatch):
    monkeypatch.setenv("ARBITRAGE_THRESHOLD", "0.06")
    cfg = load_config(None)
    assert cfg["alert_threshold_percent"] == 0.06


@pytest.mark.asyncio
async def test_run_once_async_no_tickers(monkeypatch):
    # Patch Binance/Coinbase clients to raise
    from arbitrage_notifier.main import run_once_async
    class DummyClient:
        async def get_ticker(self, _): raise Exception("fail")
    monkeypatch.setattr("arbitrage_notifier.main.BinanceClient", lambda _: DummyClient())
    monkeypatch.setattr("arbitrage_notifier.main.CoinbaseClient", lambda _: DummyClient())
    await run_once_async(DEFAULT_CONFIG)  # should run without exceptions