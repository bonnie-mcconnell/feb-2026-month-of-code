from typing import Iterable, List
import logging

from arbitrage_notifier.domain.ticker import Ticker
from arbitrage_notifier.exchanges.base_client import BaseExchangeClient


logger = logging.getLogger(__name__)


class PriceAggregator:
    """
    Coordinates multiple exchange clients and gathers ticker data.
    One exchange failure must not break the entire aggregation.
    """

    def __init__(self, clients: Iterable[BaseExchangeClient]):
        self._clients = list(clients)

        if not self._clients:
            raise ValueError("At least one exchange client is required")

    def get_tickers(self, symbol: str) -> List[Ticker]:
        tickers: List[Ticker] = []

        for client in self._clients:
            try:
                ticker = client.get_ticker(symbol)
                tickers.append(ticker)
            except Exception as exc:
                logger.warning(
                    "Exchange client failed",
                    extra={"symbol": symbol, "error": str(exc)},
                )

        return tickers