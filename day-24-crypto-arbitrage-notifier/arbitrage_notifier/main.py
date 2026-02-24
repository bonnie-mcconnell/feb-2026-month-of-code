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


def configure_logging(level: str = "INFO", json_logs: bool = False) -> None:
    if json_logs:
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format='{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}',
        )
    else:
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )


def load_config(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        return json.load(f)


def build_clients(config: Dict):
    rate_limit = config["rate_limit"]

    limiter = RateLimiter(
        capacity=rate_limit["capacity"],
        refill_rate_per_second=Decimal(str(rate_limit["refill_rate_per_second"])),
    )

    return (
        BinanceClient(limiter),
        CoinbaseClient(limiter),
    )


def run_once(config: Dict) -> None:
    logger = logging.getLogger(LOGGER_NAME)

    binance, coinbase = build_clients(config)

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
        logger.warning("No tickers available.")
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


def run_forever(config: Dict) -> None:
    logger = logging.getLogger(LOGGER_NAME)
    interval = config.get("poll_interval_seconds", 10)

    logger.info("Starting arbitrage notifier service.")
    logger.info("Polling every %s seconds.", interval)

    try:
        while True:
            run_once(config)
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Graceful shutdown requested.")


def main(config_path: Path | None = None, once: bool = False, json_logs: bool = False) -> None:
    configure_logging(json_logs=json_logs)

    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "settings.json"

    config = load_config(config_path)

    if once:
        run_once(config)
    else:
        run_forever(config)


if __name__ == "__main__":
    main()