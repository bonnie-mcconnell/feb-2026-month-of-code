from decimal import Decimal
from datetime import datetime, timezone
from arbitrage_notifier.domain.money import Money
from arbitrage_notifier.domain.ticker import Ticker
from arbitrage_notifier.services.spread_engine import compute_best_spread


def make_ticker(exchange, symbol, bid, ask):
    return Ticker(
        exchange=exchange,
        symbol=symbol,
        bid=Money(Decimal(bid)),
        ask=Money(Decimal(ask)),
        timestamp=datetime.now(timezone.utc),
    )


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


def test_multiple_exchanges_only_one_profitable_pair():
    t1 = make_ticker("binance", "BTCUSDT", "100", "101")
    t2 = make_ticker("coinbase", "BTCUSDT", "99", "102")
    t3 = make_ticker("kraken", "BTCUSDT", "105", "106")

    fees = {
        "binance": Decimal("0"),
        "coinbase": Decimal("0"),
        "kraken": Decimal("0"),
    }

    spread = compute_best_spread("BTCUSDT", [t1, t2, t3], fees)

    assert spread is not None
    assert spread.buy_exchange == "binance"
    assert spread.sell_exchange == "kraken"
    assert spread.spread_absolute.amount == Decimal("4")


def test_compute_best_spread_simple():
    tickers = [
        Ticker("binance", "BTC", Money(Decimal("100")), Money(Decimal("101")), datetime.now(timezone.utc)),
        Ticker("coinbase", "BTC", Money(Decimal("105")), Money(Decimal("106")), datetime.now(timezone.utc)),
    ]

    fees = {"binance": Decimal("0.1"), "coinbase": Decimal("0.2")}

    spread = compute_best_spread("BTC", tickers, fees)

    assert spread is not None
    assert spread.spread_percent > 0


def test_compute_best_spread_insufficient():
    assert compute_best_spread("BTC", [], {}) is None
    t = make_ticker("binance", "BTCUSDT", "100", "101")
    assert compute_best_spread("BTC", [t], {}) is None

def test_compute_best_spread_same_exchange():
    t1 = make_ticker("binance", "BTCUSDT", "100", "101")
    t2 = make_ticker("binance", "BTCUSDT", "102", "103")
    assert compute_best_spread("BTC", [t1, t2], {}) is None

def test_compute_best_spread_negative_spread():
    t1 = make_ticker("binance", "BTCUSDT", "105", "106")
    t2 = make_ticker("coinbase", "BTCUSDT", "104", "105")
    assert compute_best_spread("BTC", [t1, t2], {}) is None

def test_compute_best_spread_success():
    t1 = make_ticker("binance", "BTCUSDT", "100", "101")
    t2 = make_ticker("coinbase", "BTCUSDT", "105", "106")
    spread = compute_best_spread("BTC", [t1, t2], {"binance": Decimal("0"), "coinbase": Decimal("0")})
    assert spread is not None
    assert spread.buy_exchange == "binance"
    assert spread.sell_exchange == "coinbase"