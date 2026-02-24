import logging
from decimal import Decimal
from arbitrage_notifier.domain.spread import Spread


logger = logging.getLogger(__name__)


class AlertEngine:

    def __init__(self, threshold_percent: Decimal):
        self.threshold = threshold_percent

    def evaluate(self, spread: Spread | None) -> None:
        if spread is None:
            return

        if spread.spread_percent >= self.threshold:
            logger.info(
                "Arbitrage opportunity detected",
                extra={
                    "symbol": spread.symbol,
                    "buy_exchange": spread.buy_exchange,
                    "sell_exchange": spread.sell_exchange,
                    "spread_percent": str(spread.spread_percent),
                },
            )