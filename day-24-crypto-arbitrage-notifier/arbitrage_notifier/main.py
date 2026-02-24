import asyncio
import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Dict, Optional
from copy import deepcopy

import structlog

from arbitrage_notifier.domain.spread import Spread
from arbitrage_notifier.infra.async_rate_limiter import AsyncRateLimiter
from arbitrage_notifier.exchanges.binance_client import BinanceClient
from arbitrage_notifier.exchanges.coinbase_client import CoinbaseClient
from arbitrage_notifier.services.spread_engine import compute_best_spread
from arbitrage_notifier.services.alert_engine import AlertEngine
from arbitrage_notifier.infra.logging_config import configure_logging

logger = structlog.get_logger()


DEFAULT_CONFIG: Dict = {
    "symbols": {
        "binance": "BTCUSDT",
        "coinbase": "BTC-USD",
        "normalized": "BTC",
    },
    "fees": {
        "binance": 0.1,
        "coinbase": 0.4,
    },
    "rate_limit": {
        "capacity": 10,
        "refill_rate_per_second": 5,
    },
    "alert_threshold_percent": 0.002,  # 0.002 = 0.2%
}


def load_config(path: Path | None = None) -> Dict:
    config = deepcopy(DEFAULT_CONFIG)

    if path:
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r") as f:
            file_config = json.load(f)
            config.update(file_config)

    threshold_env = os.getenv("ARBITRAGE_THRESHOLD")
    if threshold_env:
        config["alert_threshold_percent"] = float(threshold_env)

    return config

async def run_once_async(config: Dict, dry_run: bool = False) -> None:
    logger.info("arbitrage_run_started")

    limiter = AsyncRateLimiter(
        capacity=config["rate_limit"]["capacity"],
        refill_rate_per_second=Decimal(
            str(config["rate_limit"]["refill_rate_per_second"])
        ),
    )

    binance = BinanceClient(limiter)
    coinbase = CoinbaseClient(limiter)

    tickers = []

    try:
        ticker = await binance.get_ticker(config["symbols"]["binance"])
        tickers.append(ticker)
    except Exception as e:
        logger.warning("binance_fetch_failed", error=str(e))

    try:
        ticker = await coinbase.get_ticker(config["symbols"]["coinbase"])
        tickers.append(ticker)
    except Exception as e:
        logger.warning("coinbase_fetch_failed", error=str(e))

    if len(tickers) < 2:
        logger.warning("insufficient_tickers_for_spread")
        return

    spread: Optional[Spread] = compute_best_spread(
        symbol=config["symbols"]["normalized"],
        tickers=tickers,
        fees={
            "binance": Decimal(str(config["fees"]["binance"])),
            "coinbase": Decimal(str(config["fees"]["coinbase"])),
        },
    )

    if spread is None:
        logger.info("no_profitable_spread_found")
        return

    if not dry_run:
        AlertEngine(
            threshold_percent=Decimal(
                str(config["alert_threshold_percent"])
            )
        ).evaluate(spread)
    else:
        logger.info("dry_run_enabled_alerts_skipped")

    logger.info(
        "arbitrage_run_completed",
        spread_percent=str(spread.spread_percent),
    )


async def run_continuous(config: Dict, dry_run: bool = False) -> None:
    logger.info("continuous_mode_started")

    while True:
        await run_once_async(config, dry_run=dry_run)
        await asyncio.sleep(5)  # polling interval


def main(
    config_path: Path | None = None,
    run_once: bool = False,
    dry_run: bool = False,
    symbol: str = "BTCUSDT",
    log_level: str = "INFO",
) -> None:

    configure_logging(level=log_level.upper())

    if config_path is None:
        config_path = Path("arbitrage_notifier/config/settings.json")

    config = load_config(config_path)

    # Override symbol if provided
    if symbol:
        normalized = symbol.replace("USDT", "").replace("-USD", "")
        config["symbols"]["binance"] = symbol
        config["symbols"]["coinbase"] = f"{normalized}-USD"
        config["symbols"]["normalized"] = normalized

    if run_once:
        asyncio.run(run_once_async(config, dry_run=dry_run))
    else:
        asyncio.run(run_continuous(config, dry_run=dry_run))


if __name__ == "__main__":
    main()