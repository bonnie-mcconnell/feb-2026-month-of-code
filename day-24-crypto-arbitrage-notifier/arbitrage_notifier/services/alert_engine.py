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
            # Include all info in the message string so caplog sees it
            logger.info(
                f"Arbitrage opportunity detected: {spread.symbol} "
                f"{spread.buy_exchange}->{spread.sell_exchange} "
                f"spread={spread.spread_percent}"
            )