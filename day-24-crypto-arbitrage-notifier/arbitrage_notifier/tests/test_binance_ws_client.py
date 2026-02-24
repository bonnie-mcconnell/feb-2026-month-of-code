import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from arbitrage_notifier.exchanges.binance_ws_client import BinanceWebSocketClient

@pytest.mark.asyncio
async def test_ws_stop():
    client = BinanceWebSocketClient("BTCUSDT")
    await client.stop()
    assert client._running is False

@pytest.mark.asyncio
async def test_ws_listen_cancel(monkeypatch):
    client = BinanceWebSocketClient("BTCUSDT")
    
    mock_ws = AsyncMock()
    mock_ctx = MagicMock()
    mock_ctx.__aenter__.return_value = mock_ws
    mock_ctx.__aexit__ = AsyncMock(return_value=None)
    
    monkeypatch.setattr("websockets.connect", MagicMock(return_value=mock_ctx))

    task = asyncio.create_task(client.listen())
    await asyncio.sleep(0.05) # Give it a moment to enter the loop
    
    await client.stop()
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass # Expected