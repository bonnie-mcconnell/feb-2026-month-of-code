from decimal import Decimal

from arbitrage_notifier.domain.spread import Spread
from arbitrage_notifier.domain.money import Money
from arbitrage_notifier.services.alert_engine import AlertEngine
from arbitrage_notifier.domain.ticker import Ticker


def test_alert_engine_no_spread():
    engine = AlertEngine(threshold_percent=Decimal("10"))

    # None spread should not raise
    engine.evaluate(None)

def test_alert_engine_trigger():
    engine = AlertEngine(threshold_percent=Decimal("0.01"))

    spread = Spread(
        symbol="BTC",
        buy_exchange="binance",
        sell_exchange="coinbase",
        buy_price=Money(Decimal("100")),
        sell_price=Money(Decimal("110")),
        spread_absolute=Money(Decimal("10")),
        spread_percent=Decimal("0.1"),
    )

    engine.evaluate(spread)  # Should log info, test passes if no exceptions


def make_spread(percent: Decimal) -> Spread:
    return Spread(
        symbol="BTC",
        buy_exchange="binance",
        sell_exchange="coinbase",
        buy_price=Money(Decimal("100")),
        sell_price=Money(Decimal("110")),
        spread_absolute=Money(Decimal("10")),
        spread_percent=percent,
    )


def test_alert_triggers(caplog):
    caplog.set_level("INFO")

    engine = AlertEngine(threshold_percent=Decimal("0.01"))
    spread = make_spread(Decimal("0.02"))

    engine.evaluate(spread)

    assert "Arbitrage opportunity detected" in caplog.text


def test_alert_does_not_trigger(caplog):
    engine = AlertEngine(threshold_percent=Decimal("0.05"))
    spread = make_spread(Decimal("0.02"))

    engine.evaluate(spread)

    assert "Arbitrage opportunity detected" not in caplog.text