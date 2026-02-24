import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from arbitrage_notifier.main import load_config, run_once_async, DEFAULT_CONFIG


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

    with patch(
        "arbitrage_notifier.exchanges.binance_client.BinanceClient.get_ticker",
        new_callable=AsyncMock,
    ) as mock_binance, patch(
        "arbitrage_notifier.exchanges.coinbase_client.CoinbaseClient.get_ticker",
        new_callable=AsyncMock,
    ) as mock_coinbase:

        mock_binance.return_value = AsyncMock()
        mock_coinbase.return_value = AsyncMock()

        await run_once_async(config)