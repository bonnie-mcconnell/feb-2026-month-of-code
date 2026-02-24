# Crypto Arbitrage Notifier

A production-grade asynchronous cryptocurrency arbitrage monitoring service.

This system ingests live market data from Binance (WebSocket) and Coinbase (REST), computes fee-adjusted spreads, triggers alerts when thresholds are exceeded, exposes operational metrics, and provides a REST API for observability.

This is not a trading bot. It detects and reports spread opportunities only.

---

## Core Capabilities

• Real-time price ingestion
• Binance bookTicker WebSocket stream
• Coinbase REST order book polling
• Fee-adjusted spread calculation
• Configurable alert thresholds
• Async rate limiting (token bucket)
• Redis-backed caching of latest spread
• Prometheus metrics
• Structured logging
• Dockerized deployment
• Fully async architecture (no blocking calls)
• Unit tested with pytest

## Architecture
```
Binance WS  ─┐
              ├─> PriceAggregator ─> SpreadEngine ─> AlertEngine
Coinbase REST ┘                                   │
                                                   ├─> Redis Cache
                                                   ├─> Prometheus Metrics
                                                   └─> Structured Logs

FastAPI API exposes:
  /health
  /ready
  /spread
  /metrics
```

## Project Structure
```
arbitrage_notifier/
├── api/                # FastAPI application & endpoints
├── exchanges/          # Binance + Coinbase clients (REST + WS)
├── services/           # Aggregation, spread calc, alerts
├── infra/              # Redis cache, rate limiter, logging
├── domain/             # Money, Ticker, Spread models
├── main.py             # Background spread loop orchestration
├── cli.py              # CLI entrypoint
└── tests/              # Pytest test suite
```

## Configuration

Configuration is stored in `arbitrage_notifier/config/settings.json`.

Example:
```json
{
  "symbols": {
    "binance": "BTCUSDT",
    "coinbase": "BTC-USD",
    "normalized": "BTC"
  },
  "fees": {
    "binance": 0.1,
    "coinbase": 0.4
  },
  "alert_threshold_percent": 0.002,
  "rate_limit": {
    "capacity": 10,
    "refill_rate_per_second": 5
  }
}
```

Configurable:
- Exchange symbols
- Exchange fee percentages
- Arbitrage threshold
- Poll interval
- API rate limiting parameters

## Local Development Setup
### 1. Create virtual environment

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```
Mac/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

## Running the FastAPI API

Development mode:
```bash
uvicorn arbitrage_notifier.api.app:app \
  --host 127.0.0.1 \
  --port 8000 \
  --reload \
  --timeout-keep-alive 5
```

Production-style:
```bash
uvicorn arbitrage_notifier.api.app:app \
  --host 0.0.0.0 \
  --port 8000
```

## API Endpoints
### GET /health

Liveness probe.

Returns:
```json
{
  "status": "ok",
  "redis": "up" | "down"
}
```

### GET /ready

Readiness probe for background processing.
```json
{
  "status": "ready"
}
```

### GET /spread

Returns latest cached spread.

If Redis unavailable or no spread yet:
```bash
{
  "status": "no_data"
}
```

### GET /metrics

Prometheus metrics endpoint.

Includes arbitrage_runs_total, Python GC metrics and process metrics.

## CLI Usage

View help:
```bash
python -m arbitrage_notifier.cli --help
```

Run once:
```bash
python -m arbitrage_notifier.cli --run-once
```

Dry run (no alerts):
```bash
python -m arbitrage_notifier.cli --dry-run
```

Override symbol:
```bash
python -m arbitrage_notifier.cli --symbol BTCUSDT
```

By default, CLI runs in continuous mode.
Use --run-once to execute a single arbitrage check and exit.
For continuous background monitoring, you can also run the FastAPI application.

## Background Loop (Without API)

Run spread loop directly:
```bash
python -m arbitrage_notifier.main
```

This starts the continuous polling loop which:
- Fetches prices from Binance and Coinbase
- Computes spreads
- Triggers alerts
- Updates Redis cache

## Docker Deployment
### Build + run with compose
```bash
docker-compose down --volumes --remove-orphans
docker-compose up --build
```

This starts:
- FastAPI app (port 8000)
- Redis (port 6379)

Then test:
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
curl http://127.0.0.1:8000/spread
curl http://127.0.0.1:8000/metrics
```

If Redis is unavailable:
- /health will report redis: "down"
- /spread returns {"status":"no_data"}
- Application continues running

### Manual Docker Build
```bash
docker build -t crypto-arb-notifier .
docker run -p 8000:8000 crypto-arb-notifier
```

## Testing

Run full test suite with coverage:
```bash
pytest --cov=arbitrage_notifier --cov-report=term-missing
```

Tests include:
- Exchange client behavior
- Rate limiter
- Spread calculation
- API endpoints
- Error handling

Target coverage: ≥ 90%
Currently at 91%.
Uncovered lines include: API background lifecycle, continuous loop branch, some Websocket reconnect paths.

## Observability

Structured logging via structlog
Prometheus metrics via /metrics
Graceful shutdown of async tasks
Redis health reporting
WebSocket cancellation handling

## Production Design

- Fully async (no blocking I/O)
- Background task orchestration via FastAPI lifespan
- Graceful task cancellation
- External dependency isolation
- Failure-tolerant Redis access
- Rate-limited external API calls
- WebSocket reconnect handling
- Clean Dockerized deployment

---

This system:
- Does not execute trades
- Does not predict price direction
- Does not provide financial advice

It strictly monitors and reports cross-exchange spreads.

## License

MIT