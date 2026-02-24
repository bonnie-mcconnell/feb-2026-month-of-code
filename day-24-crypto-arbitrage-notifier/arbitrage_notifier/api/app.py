import asyncio
from decimal import Decimal
from typing import Optional
import structlog
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest

from arbitrage_notifier.main import DEFAULT_CONFIG
from arbitrage_notifier.infra.async_rate_limiter import AsyncRateLimiter
from arbitrage_notifier.exchanges.binance_client import BinanceClient
from arbitrage_notifier.exchanges.coinbase_client import CoinbaseClient
from arbitrage_notifier.exchanges.binance_ws_client import BinanceWebSocketClient
from arbitrage_notifier.infra.cache import RedisCache
from arbitrage_notifier.services.spread_engine import compute_best_spread
from arbitrage_notifier.services.alert_engine import AlertEngine

logger = structlog.get_logger()
config = DEFAULT_CONFIG.copy()
cache = RedisCache()
ws_client = BinanceWebSocketClient(config["symbols"]["binance"])
background_task: Optional[asyncio.Task] = None

REQUEST_COUNT = Counter(
    "arbitrage_runs_total",
    "Total arbitrage executions"
)

# -------------------------------------------------
# BACKGROUND LOOP
# -------------------------------------------------
async def spread_loop():
    logger.info("spread_loop_started")
    limiter = AsyncRateLimiter(
        capacity=config["rate_limit"]["capacity"],
        refill_rate_per_second=Decimal(str(config["rate_limit"]["refill_rate_per_second"]))
    )
    binance = BinanceClient(limiter)
    coinbase = CoinbaseClient(limiter)

    while True:
        try:
            REQUEST_COUNT.inc()
            tickers = []
            if ws_client.latest_ticker:
                tickers.append(ws_client.latest_ticker)
            try:
                ticker = await coinbase.get_ticker(config["symbols"]["coinbase"])
                tickers.append(ticker)
            except Exception as e:
                logger.warning("coinbase_fetch_failed", error=str(e))
            if len(tickers) < 2:
                await asyncio.sleep(1)
                continue

            spread = compute_best_spread(
                symbol=config["symbols"]["normalized"],
                tickers=tickers,
                fees={
                    "binance": Decimal(str(config["fees"]["binance"])),
                    "coinbase": Decimal(str(config["fees"]["coinbase"]))
                },
            )

            if spread is None:
                await asyncio.sleep(1)
                continue

            await cache.set("latest_spread", str(spread.spread_percent))

            AlertEngine(threshold_percent=Decimal(str(config["alert_threshold_percent"]))).evaluate(spread)

        except asyncio.CancelledError:
            logger.info("spread_loop_cancelled")
            break
        except Exception as e:
            logger.exception("spread_loop_error", error=str(e))
        await asyncio.sleep(1)

# -------------------------------------------------
# LIFESPAN / STARTUP-SHUTDOWN
# -------------------------------------------------
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    global background_task
    # Startup
    await ws_client.listen()
    background_task = asyncio.create_task(spread_loop())
    logger.info("application_started")
    yield
    # Shutdown
    await ws_client.stop()
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
    logger.info("application_shutdown_complete")

app = FastAPI(title="Crypto Arbitrage Notifier", lifespan=lifespan)

# -------------------------------------------------
# HEALTH / READINESS / DATA ROUTES
# -------------------------------------------------
@app.get("/health")
async def health():
    redis_status = "down"
    try:
        await cache.ping()
        redis_status = "ok"
    except Exception:
        pass
    return {"status": "ok", "redis": redis_status}

@app.get("/ready")
async def readiness():
    if background_task is None or background_task.done():
        return {"status": "not_ready"}
    return {"status": "ready"}

@app.get("/spread")
async def get_spread():
    spread = await cache.get("latest_spread")
    return {"spread": spread}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")