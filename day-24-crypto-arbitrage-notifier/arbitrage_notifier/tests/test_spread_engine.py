from decimal import Decimal
from datetime import datetime, timezone
from domain.money import Money
from domain.ticker import Ticker


def make_ticker(exchange, symbol, bid, ask):
    return Ticker(
        exchange=exchange,
        symbol=symbol,
        bid=Money(Decimal(bid)),
        ask=Money(Decimal(ask)),
        timestamp=datetime.now(timezone.utc),
    )

from services.spread_engine import compute_best_spread


def test_positive_spread_no_fees():
    t1 = make_ticker("binance", "BTCUSDT", "42000", "42100")
    t2 = make_ticker("coinbase", "BTCUSDT", "42300", "42400")

    fees = {
        "binance": Decimal("0"),
        "coinbase": Decimal("0"),
    }

    spread = compute_best_spread("BTCUSDT", [t1, t2], fees)

    assert spread is not None
    assert spread.buy_exchange == "binance"
    assert spread.sell_exchange == "coinbase"
    assert spread.spread_absolute.amount == Decimal("200")


def test_negative_spread_returns_none():
    t1 = make_ticker("binance", "BTCUSDT", "42000", "42100")
    t2 = make_ticker("coinbase", "BTCUSDT", "41900", "42000")

    fees = {"binance": Decimal("0"), "coinbase": Decimal("0")}

    spread = compute_best_spread("BTCUSDT", [t1, t2], fees)

    assert spread is None


def test_fees_eliminate_spread():
    t1 = make_ticker("binance", "BTCUSDT", "42000", "42100")
    t2 = make_ticker("coinbase", "BTCUSDT", "42300", "42400")

    fees = {
        "binance": Decimal("1.0"),   # 1%
        "coinbase": Decimal("1.0"),  # 1%
    }

    spread = compute_best_spread("BTCUSDT", [t1, t2], fees)

    assert spread is None


def test_same_exchange_returns_none():
    t1 = make_ticker("binance", "BTCUSDT", "42000", "42100")
    t2 = make_ticker("binance", "BTCUSDT", "42300", "42400")

    fees = {"binance": Decimal("0")}

    spread = compute_best_spread("BTCUSDT", [t1, t2], fees)

    assert spread is None


def test_spread_percent_calculation():
    t1 = make_ticker("binance", "BTCUSDT", "100", "100")
    t2 = make_ticker("coinbase", "BTCUSDT", "110", "110")

    fees = {"binance": Decimal("0"), "coinbase": Decimal("0")}

    spread = compute_best_spread("BTCUSDT", [t1, t2], fees)

    assert spread is not None  # required for typing

    assert spread.spread_absolute.amount == Decimal("10")
    assert spread.spread_percent == Decimal("0.1")


def test_global_min_max_same_exchange_but_valid_cross_exists():
    # Binance has best bid AND best ask
    t1 = make_ticker("binance", "BTCUSDT", "105", "106")
    t2 = make_ticker("coinbase", "BTCUSDT", "104", "107")
    t3 = make_ticker("kraken", "BTCUSDT", "103", "108")

    fees = {
        "binance": Decimal("0"),
        "coinbase": Decimal("0"),
        "kraken": Decimal("0"),
    }

    spread = compute_best_spread("BTCUSDT", [t1, t2, t3], fees)

    assert spread is not None
    assert spread.buy_exchange == "coinbase"
    assert spread.sell_exchange == "binance"
    assert spread.spread_absolute.amount == Decimal("105") - Decimal("107")  # <-- NO