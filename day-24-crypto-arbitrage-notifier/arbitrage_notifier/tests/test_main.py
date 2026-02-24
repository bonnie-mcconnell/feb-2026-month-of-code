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