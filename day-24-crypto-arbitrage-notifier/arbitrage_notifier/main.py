import logging
from decimal import Decimal

from infra.rate_limiter import RateLimiter
from exchanges.binance_client import BinanceClient
from exchanges.coinbase_client import CoinbaseClient
from services.price_aggregator import PriceAggregator
from services.spread_engine import compute_best_spread
from services.alert_engine import AlertEngine


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main():
    configure_logging()

    symbol_binance = "BTCUSDT"
    symbol_coinbase = "BTC-USD"

    binance = BinanceClient(
        RateLimiter(capacity=10, refill_rate_per_second=Decimal("5"))
    )

    coinbase = CoinbaseClient(
        RateLimiter(capacity=10, refill_rate_per_second=Decimal("5"))
    )

    aggregator = PriceAggregator([binance, coinbase])

    tickers = []

    try:
        tickers.append(binance.get_ticker(symbol_binance))
    except Exception:
        pass

    try:
        tickers.append(coinbase.get_ticker(symbol_coinbase))
    except Exception:
        pass

    spread = compute_best_spread(
        symbol="BTC",
        tickers=tickers,
        fees={
            "binance": Decimal("0.1"),
            "coinbase": Decimal("0.4"),
        },
    )

    alert_engine = AlertEngine(threshold_percent=Decimal("0.002"))

    alert_engine.evaluate(spread)


if __name__ == "__main__":
    main()


    