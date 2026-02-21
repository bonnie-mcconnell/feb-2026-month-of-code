# Metrics Aggregation Dashboard

A type-safe, extensible metrics ingestion and risk scoring engine for aggregating operational health across multiple services.

Built with:
- TypeScript (strict mode)
- Node.js
- Express
- Deterministic scoring engine
- Multi-project portfolio aggregation
- CLI + API + HTML reporting
- Docker + CI ready

## What This Project Does

This system ingests service-level operational metrics such as:
- Uptime
- Job processing reliability
- Repository complexity
- Contributor health

It then:
- Normalizes metrics
- Scores each subsystem (0–100)
- Calculates risk tiers
- Produces a portfolio-wide dashboard
- Exports JSON, CLI, and HTML heatmap reports
- Serves metrics via REST API

## Architecture
```
src/
  aggregation/       → scoring + risk engine
  ingestion/         → JSON & CSV adapters
  reporters/         → HTML / CLI / JSON output
  config/            → subsystem weight overrides
  schema/            → unified metrics contracts
  cli/               → command-line interface
  server.ts          → Express API entrypoint
```

## Core Concepts

| Layer       | Responsibility                              |
| ----------- | ------------------------------------------- |
| Ingestion   | Parse raw JSON/CSV into typed domain inputs |
| Aggregation | Deterministic scoring + risk evaluation     |
| Schema      | Strict UnifiedMetricsV1 contract            |
| Reporting   | Multiple output formats                     |
| API         | Serve dashboard via REST                    |

## Installation
```bash
npm install
```

Build:
```bash
npm run build
```

## Example Metrics Structure
```
tests/fixtures/portfolio/
  service-a/
    uptime.json
    jobs.json
    repo-index.json
    health-report.json

  service-b/
    uptime.json
    jobs.csv
    repo-index.json
    health-report.json
```

Supports:
- `jobs.json`
- OR `jobs.csv` (via CSV ingestion adapter)

## CLI Usage
### Generate JSON + HTML
```bash
node dist/cli.js tests/fixtures/portfolio --json --html
```

### CLI Console Report
```bash
node dist/cli.js tests/fixtures/portfolio --cli
```

### Custom Config (override subsystem weights)
```bash
node dist/cli.js tests/fixtures/portfolio --config myconfig.json --json
```

### Start API Server
```bash
node dist/cli.js --server
```

Custom port:
```bash
node dist/cli.js --server --port 5000
```

## API

Start server:
```bash
node dist/cli.js --server
```

Access:
```
GET http://localhost:3000/api/dashboard
```

Returns full portfolio dashboard JSON.

## Scoring Model

Each subsystem produces a 0–100 score.

Portfolio-level metrics are weighted:
```
overallHealthScore =
  uptimeWeight * uptimeScore +
  jobsWeight * jobReliabilityScore +
  repositoryWeight * maintainabilityScore +
  repoHealthWeight * activityScore
```

Risk tiers:

| Score  | Tier   |
| ------ | ------ |
| 80–100 | LOW    |
| 50–79  | MEDIUM |
| <50    | HIGH   |

## Testing

Run:
```bash
npm test
```

Includes:
- Aggregation engine unit tests
- Integration tests using fixture portfolio
- Risk tier validation

## Docker

Build:
```bash
docker build -t metrics-dashboard .
```

Run:
```bash
docker run -p 3000:3000 metrics-dashboard
```

## CI

The repository includes:
- TypeScript strict build check
- Test execution
- Docker build validation

All must pass before merge.

## Design Principles

- No any
- Strict type contracts
- Deterministic scoring
- Optional subsystem handling
- Fail-fast parsing
- Clean separation of concerns
- Extensible ingestion adapters

## Future Enhancements

- Historical trend analysis
- Prometheus ingestion adapter
- GitHub API ingestion
- Persistent storage (Postgres)
- React dashboard frontend
- Role-based API access