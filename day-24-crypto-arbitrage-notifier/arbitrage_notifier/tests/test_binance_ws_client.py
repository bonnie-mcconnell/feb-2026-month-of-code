import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock
from arbitrage_notifier.exchanges.binance_ws_client import BinanceWebSocketClient
from decimal import Decimal

@pytest.mark.asyncio
async def test_listen_reconnect(monkeypatch):
    client = BinanceWebSocketClient("BTCUSDT")
    
    # Mock websockets.connect to raise ConnectionClosed once, then succeed
    mock_ws = AsyncMock()
    mock_ctx = MagicMock()
    mock_ctx.__aenter__.return_value = mock_ws
    mock_ctx.__aexit__ = AsyncMock(return_value=None)
    
    def connect_side_effect(*args, **kwargs):
        if not hasattr(connect_side_effect, "called"):
            connect_side_effect.called = True
            raise OSError("Connection failed")
        return mock_ctx
    
    monkeypatch.setattr("websockets.connect", connect_side_effect)
    
    task = asyncio.create_task(client.listen())
    await asyncio.sleep(0.05)
    
    await client.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_listen_process_message(monkeypatch):
    client = BinanceWebSocketClient("BTCUSDT")
    
    mock_ws = AsyncMock()
    mock_ws.__aiter__.return_value = iter([json.dumps({"b": "100", "a": "110"})])
    mock_ctx = MagicMock()
    mock_ctx.__aenter__.return_value = mock_ws
    mock_ctx.__aexit__ = AsyncMock(return_value=None)
    
    monkeypatch.setattr("websockets.connect", lambda url, **kwargs: mock_ctx)
    
    task = asyncio.create_task(client.listen())
    await asyncio.sleep(0.05)
    
    assert client.latest_ticker is not None
    assert client.latest_ticker.bid.amount == Decimal("100")
    
    await client.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

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