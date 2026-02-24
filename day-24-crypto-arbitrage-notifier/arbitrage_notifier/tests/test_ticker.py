import pytest
from decimal import Decimal
from datetime import datetime, timezone
from arbitrage_notifier.domain.ticker import Ticker
from arbitrage_notifier.domain.money import Money


def test_ticker_ask_lower_than_bid():
    with pytest.raises(ValueError):
        Ticker(
            exchange="binance",
            symbol="BTC",
            bid=Money(Decimal("101")),
            ask=Money(Decimal("100")),
            timestamp=datetime.utcnow(),
        )

def test_ticker_non_utc_timestamp():
    from datetime import timezone
    with pytest.raises(ValueError):
        Ticker(
            exchange="binance",
            symbol="BTC",
            bid=Money(Decimal("100")),
            ask=Money(Decimal("101")),
            timestamp=datetime.now(),
        )
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