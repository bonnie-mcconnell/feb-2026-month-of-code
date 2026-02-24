from datetime import datetime, timezone
from decimal import Decimal
from arbitrage_notifier.domain.ticker import Ticker
from arbitrage_notifier.domain.money import Money

def test_ticker_repr():
    timestamp = datetime.now(timezone.utc)
    ticker = Ticker(
        exchange="binance",
        symbol="BTCUSDT",
        bid=Money(Decimal("100")),
        ask=Money(Decimal("101")),
        timestamp=timestamp
    )
    assert repr(ticker) is not None
    # Also check post-init validations
    assert ticker.ask.amount >= ticker.bid.amount
    assert ticker.timestamp.tzinfo == timezone.utc