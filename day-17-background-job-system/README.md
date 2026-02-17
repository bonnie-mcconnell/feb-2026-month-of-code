# Background Job Worker System

A fully-featured, Redis-backed job queue and worker system built in TypeScript.

---

## Features

- **Redis-backed queue** with pending, processing, and dead-letter queues.
- **Worker** with:
  - Concurrency control
  - Retry policy with exponential backoff
  - Idempotency via in-memory store
  - Circuit breaker support
  - Rate limiting
  - Job timeouts
- **Observability**:
  - Console logging
  - Metrics export in Prometheus format
  - OpenTelemetry tracing (optional)
- **HTTP API**:
  - `GET /health` — returns `{status: "ok"}`
  - `POST /enqueue` — enqueue jobs
  - `GET /metrics` — Prometheus metrics

---

## Getting Started

### Requirements

- Node.js 18+
- npm
- Docker (for Redis)

### Install dependencies

```bash
npm install
```

### Run Redis locally
```bash
docker-compose up -d redis
```

### Run the worker & API
```bash
npm run dev
```

## API Usage
### Health Check
```bash
Invoke-WebRequest http://localhost:3000/health -UseBasicParsing
```

### Enqueue Job
```bash
Invoke-WebRequest http://localhost:3000/enqueue `
  -Method POST `
  -Body (@{name="test"; payload=@{foo="bar"}} | ConvertTo-Json) `
  -ContentType "application/json" `
  -UseBasicParsing
```

### Get Metrics
```
Invoke-WebRequest http://localhost:3000/metrics -UseBasicParsing
```

## Testing

The project uses tests/ directory for unit/integration tests.
Run them with:
```bash
npm install --save-dev jest ts-jest @types/jest
npx jest
```

## Shutdown

Press Ctrl+C to stop the worker. The system will:

- Stop accepting new jobs
- Complete active jobs
- Close HTTP server
- Quit Redis connection gracefully

## Future Additions

- Add full CI pipeline (GitHub Actions)
- Add real Prometheus + Grafana docker stack
- Add load testing with k6
- Convert this into a SaaS-ready background job service