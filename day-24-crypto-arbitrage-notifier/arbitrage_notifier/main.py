import logging
import time
import json
from decimal import Decimal
from pathlib import Path
from typing import Dict

from arbitrage_notifier.infra.rate_limiter import RateLimiter
from arbitrage_notifier.exchanges.binance_client import BinanceClient
from arbitrage_notifier.exchanges.coinbase_client import CoinbaseClient
from arbitrage_notifier.services.price_aggregator import PriceAggregator
from arbitrage_notifier.services.spread_engine import compute_best_spread
from arbitrage_notifier.services.alert_engine import AlertEngine


LOGGER_NAME = "arbitrage_notifier"


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def load_config() -> Dict:
    config_path = Path(__file__).parent.parent / "config" / "settings.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        return json.load(f)


def build_clients(config: Dict):
    binance = BinanceClient(
        RateLimiter(
            capacity=config["rate_limit"]["capacity"],
            refill_rate_per_second=Decimal(
                str(config["rate_limit"]["refill_rate_per_second"])
            ),
        )
    )

    coinbase = CoinbaseClient(
        RateLimiter(
            capacity=config["rate_limit"]["capacity"],
            refill_rate_per_second=Decimal(
                str(config["rate_limit"]["refill_rate_per_second"])
            ),
        )
    )

    return binance, coinbase


def run_once(config: Dict) -> None:
    logger = logging.getLogger(LOGGER_NAME)

    binance, coinbase = build_clients(config)

    aggregator = PriceAggregator([binance, coinbase])

    tickers = []

    try:
        tickers.append(binance.get_ticker(config["symbols"]["binance"]))
    except Exception as e:
        logger.warning("Binance fetch failed: %s", e)

    try:
        tickers.append(coinbase.get_ticker(config["symbols"]["coinbase"]))
    except Exception as e:
        logger.warning("Coinbase fetch failed: %s", e)

    if not tickers:
        logger.warning("No tickers available, skipping spread computation.")
        return

    spread = compute_best_spread(
        symbol=config["symbols"]["normalized"],
        tickers=tickers,
        fees={
            "binance": Decimal(str(config["fees"]["binance"])),
            "coinbase": Decimal(str(config["fees"]["coinbase"])),
        },
    )

    alert_engine = AlertEngine(
        threshold_percent=Decimal(str(config["alert_threshold_percent"]))
    )

    alert_engine.evaluate(spread)


def main() -> None:
    configure_logging()

    logger = logging.getLogger(LOGGER_NAME)

    config = load_config()

    interval = config.get("poll_interval_seconds", 10)

    logger.info("Starting arbitrage notifier service.")
    logger.info("Polling interval: %s seconds", interval)

    try:
        while True:
            run_once(config)
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Shutdown requested. Exiting gracefully.")


if __name__ == "__main__":
    main()