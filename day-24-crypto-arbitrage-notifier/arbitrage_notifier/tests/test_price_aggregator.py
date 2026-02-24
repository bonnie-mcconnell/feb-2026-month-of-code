from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import Mock

from arbitrage_notifier.services.price_aggregator import PriceAggregator
from arbitrage_notifier.domain.ticker import Ticker
from arbitrage_notifier.domain.money import Money


def make_ticker(exchange: str) -> Ticker:
    return Ticker(
        exchange=exchange,
        symbol="BTCUSDT",
        bid=Money(Decimal("100")),
        ask=Money(Decimal("101")),
        timestamp=datetime.now(timezone.utc),
    )


def test_aggregator_collects_multiple_clients():
    c1 = Mock()
    c2 = Mock()

    c1.get_ticker.return_value = make_ticker("binance")
    c2.get_ticker.return_value = make_ticker("kraken")

    aggregator = PriceAggregator([c1, c2])
    result = aggregator.get_tickers("BTCUSDT")

    assert len(result) == 2


def test_aggregator_isolates_failures():
    c1 = Mock()
    c2 = Mock()

    c1.get_ticker.return_value = make_ticker("binance")
    c2.get_ticker.side_effect = RuntimeError("boom")

    aggregator = PriceAggregator([c1, c2])
    result = aggregator.get_tickers("BTCUSDT")

    assert len(result) == 1
    assert result[0].exchange == "binance"


def test_aggregator_requires_clients():
    import pytest

    with pytest.raises(ValueError):
        PriceAggregator([])