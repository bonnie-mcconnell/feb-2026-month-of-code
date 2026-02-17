# Background Job System

## Features

- In-memory queue
- Worker runtime with concurrency
- Exponential retry
- Dead-letter support
- Idempotency protection
- Structured logging
- Prometheus metrics
- Graceful shutdown

## Run

npm install
npm run build
node dist/index.js

## Endpoints

GET /health
GET /metrics
POST /enqueue

## Example

curl -X POST http://localhost:3000/enqueue \
  -H "Content-Type: application/json" \
  -d '{"name":"test","payload":{"a":1}}'
