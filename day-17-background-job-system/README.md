# Background Job Worker System

A production-style background job processing system built in TypeScript, designed to model real-world distributed worker architecture.

This project demonstrates retry strategies, idempotency guarantees, failure handling, observability, and clean runtime/test separation.

## Overview

This system consists of:
- A Redis-backed job queue
- A configurable worker with concurrency control
- Retry + exponential backoff policy
- Idempotency enforcement
- Dead-letter handling
- Job timeouts
- Metrics export (Prometheus format)
- HTTP API for enqueueing and health checks
- Graceful shutdown behavior

It is structured to mimic how production background processing systems operate.

## Architecture
### 1. Queue Abstraction

The worker depends on a Queue interface rather than a concrete implementation.

Implementations:
- RedisQueue (production)
- InMemoryQueue (testing)

This allows:
- Test isolation without Redis
- Clean separation of infrastructure from domain logic

### 2. Worker Model

The worker:
- Polls the queue at a configurable interval
- Processes jobs with configurable concurrency
- Applies a retry policy on failure
- Moves exhausted jobs to a dead-letter queue
- Tracks metrics for:
  - Completed jobs
  - Failed jobs
  - Retries
  - Dead-lettered jobs
  - Idempotent skips

Concurrency and retry behavior are configurable.

### 3. Retry Strategy

Retries are handled via a pluggable RetryPolicy.

Current implementation:
- Exponential backoff
- Max retry limit

This design allows swapping in alternative retry strategies.

### 4. Idempotency

Jobs may include an idempotencyKey.

If a job with the same key has already been processed:
- It is skipped
- A metric is incremented

This prevents duplicate work in distributed systems scenarios.

### 5. Timeouts

Jobs are subject to a maximum execution time.

If a job exceeds jobTimeoutMs:
- It is treated as failed
- Retry policy applies

This prevents stuck or long-running tasks from blocking worker throughput.

### 6. Observability

Includes:
- Structured logging (ConsoleLogger abstraction)
- In-memory metrics store
- Prometheus-compatible /metrics endpoint
- Optional OpenTelemetry tracing bootstrap

Metrics exposed include:
- jobs_completed_total
- jobs_failed_total
- jobs_retried_total
- jobs_dead_lettered_total
- jobs_skipped_idempotent

### 7. Graceful Shutdown

On SIGINT or SIGTERM:
- Worker stops polling
- In-flight jobs complete
- HTTP server closes
- Redis connection closes

This models production-safe shutdown behavior.

## HTTP API
GET /health

Returns:
```json
{ "status": "ok" }
```

POST /enqueue

Request:
```json
{
  "name": "example-job",
  "payload": { "foo": "bar" },
  "idempotencyKey": "optional-key"
}
```

Response:
```json
{
  "enqueued": "<job-id>"
}
```

GET /metrics

Returns Prometheus-formatted metrics.

### Running Locally
#### Requirements

- Node.js 18+
- Docker (for Redis)

### Install
```bash
npm install
```

Start Redis
```bash
docker-compose up -d redis
```

Start API + Worker
```bash
npm run dev
```

Server runs on:
```bash
http://localhost:3000
```

### Testing Strategy

This project includes:
- Unit tests for worker behavior
- Integration tests for HTTP endpoints
- In-memory queue for deterministic test isolation
- No external services required for test execution

Run tests:
```bash
npm test
```

All tests should pass without Redis running.

## Design Decisions
### Why Abstract the Queue?

To decouple worker logic from infrastructure.
This allows:
- Fast unit tests
- Easier future migration to other backends (SQS, Kafka, etc)

### Why Separate Bootstrap From App?

The HTTP app is exported without side effects.

Redis connections and worker startup occur only in bootstrap().

This prevents:
- Test hangs
- External dependency coupling
- Hidden side effects during import

### Why In-Memory Metrics?

To simulate Prometheus-style counters without external dependencies.

In production, this could be replaced with:
- prom-client
- OpenTelemetry metrics
- StatsD

## Future Improvements

- Replace polling with Redis blocking operations (e.g BRPOP)
- Persistent idempotency store (Redis-backed)
- Real Prometheus + Grafana stack
- Distributed multi-worker deployment
- CI pipeline
- Load testing

## What This Project Demonstrates

- Asynchronous processing
- Failure modeling
- Retry semantics
- Idempotency design
- Dependency inversion
- Observability integration
- Graceful shutdown patterns
- Testable infrastructure design

This project intentionally focuses on backend systems design rather than UI or CRUD patterns.
