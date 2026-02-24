# Crypto Arbitrage Notifier

A production-grade **cryptocurrency arbitrage notifier**. This system monitors prices across multiple exchanges, computes spreads, and logs arbitrage opportunities when thresholds are exceeded. Designed for backend data pipelines, monitoring, and alerting — not for trading or prediction.

---

## Features

- Real-time **price monitoring** from Binance (WebSocket) and Coinbase (REST API)
- **Spread calculation** with configurable fees
- **Alerting engine** when spreads exceed thresholds
- **Async rate limiting** for API calls
- **Caching** latest spreads in Redis
- **Prometheus metrics** for observability
- Fully **test-covered**, production-grade async Python

---

## Architecture Overview

- **API**: FastAPI application exposing `/health`, `/ready`, `/spread`, `/metrics`
- **Background loop**: Pulls prices, calculates spreads, triggers alerts
- **Exchanges**: Binance WebSocket, Binance REST, Coinbase REST
- **Services**: `AlertEngine`, `SpreadEngine`, `PriceAggregator`
- **Infra**: Redis cache, async rate limiter, structured logging

---

## Installation

1. Clone repo (currently this is in a folder so this is unavailable):
```bash
git clone <repo-url>
cd day-24-crypto-arbitrage-notifier
```

Create virtualenv:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Configuration

DEFAULT_CONFIG located in main.py or use config/settings.json

Configure:

Symbols: BTCUSDT, ETHUSDT, etc.

Fees per exchange

Rate limiting: capacity & refill rate

Alert threshold percent

Running the Application
FastAPI API
uvicorn arbitrage_notifier.api.app:app --reload

Endpoints

/health → Redis and system status

/ready → Readiness for processing

/spread → Latest computed spread

/metrics → Prometheus metrics

CLI
python -m arbitrage_notifier.cli --help
Main Loop
python -m arbitrage_notifier.main

Starts async background loop for spread computation and alerting


# TODO add all other flags/correct commands e.g cli.main vs .main (not cli)
Docker
docker build -t crypto-arb-notifier .
docker run -p 8000:8000 crypto-arb-notifier
Testing

Run all tests:

pytest --cov=arbitrage_notifier --cov-report=term-missing

Manual API testing:

curl http://localhost:8000/health
curl http://localhost:8000/spread
Project Structure
arbitrage_notifier/
├─ api/                   # FastAPI endpoints
├─ cli.py                 # CLI entrypoint
├─ domain/                # Money, Ticker, Spread models
├─ exchanges/             # Binance/Coinbase clients, WS client
├─ infra/                 # Cache, rate limiter, retry, logging
├─ services/              # AlertEngine, SpreadEngine, PriceAggregator
├─ main.py                # Background loop orchestration
├─ tests/                 # Pytest unit tests
└─ requirements.txt
Observability

Prometheus metrics available at /metrics

Structured logging via structlog

Alerts logged when arbitrage thresholds are exceeded

Notes

Not a trading bot — only detects and logs opportunities

Designed for modularity, async execution, and production-quality observability

Fully covered by unit tests (~94% coverage)

Redis required for caching

License

MIT License

# TO ADD

Architecture diagram showing: Exchanges → Price Aggregator → Spread Engine → Alerts → Redis / Prometheus / API.

CLI Examples:

python -m arbitrage_notifier.cli --run-once
python -m arbitrage_notifier.cli --dry-run --symbol BTCUSDT

Docker / Compose Examples:

docker build -t crypto-arb-notifier .
docker run -p 8000:8000 crypto-arb-notifier

docker-compose up --build

API Example Requests (curl / HTTPie)

Logging / Alerts explanation with sample JSON logs

Testing Instructions:

pytest --cov=arbitrage_notifier --cov-report=term-missing

Production Readiness Notes:

Async-safe

Reconnects WebSocket automatically

Rate-limited API requests

Prometheus observability

Configurable fees and thresholds



- uvicorn arbitrage_notifier.api.app:app --host 0.0.0.0 --port 8000 --reload --timeout-keep-alive 5