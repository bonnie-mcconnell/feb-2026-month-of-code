import asyncio
import json
from decimal import Decimal
from datetime import datetime, timezone
import structlog
import websockets
from websockets.exceptions import ConnectionClosed

from arbitrage_notifier.domain.ticker import Ticker
from arbitrage_notifier.domain.money import Money


logger = structlog.get_logger()


class BinanceWebSocketClient:
    BASE_URL = "wss://stream.binance.com:9443/ws"

    def __init__(self, symbol: str):
        self.symbol = symbol.lower()
        self.url = f"{self.BASE_URL}/{self.symbol}@bookTicker"
        self.latest_ticker: Ticker | None = None
        self._running = False

    async def listen(self) -> None:
        """
        Persistent listener with automatic reconnect.
        """
        self._running = True
        backoff = 1

        while self._running:
            try:
                logger.info("binance_ws_connecting", url=self.url)

                async with websockets.connect(self.url, ping_interval=20) as ws:
                    logger.info("binance_ws_connected")
                    backoff = 1  # reset backoff after success

                    async for message in ws:
                        data = json.loads(message)

                        bid = Decimal(data["b"])
                        ask = Decimal(data["a"])

                        self.latest_ticker = Ticker(
                            exchange="binance",
                            symbol=self.symbol.upper(),
                            bid=Money(bid),
                            ask=Money(ask),
                            timestamp=datetime.now(timezone.utc),
                        )

            except (ConnectionClosed, OSError) as e:
                logger.warning("binance_ws_disconnected", error=str(e))
            except asyncio.CancelledError:
                logger.info("binance_ws_cancelled")
                break
            except Exception as e:
                logger.exception("binance_ws_unexpected_error", error=str(e))

            logger.info("binance_ws_reconnecting", backoff=backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)

        logger.info("binance_ws_stopped")

    async def stop(self) -> None:
        self._running = False