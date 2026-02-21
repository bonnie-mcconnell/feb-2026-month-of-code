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
  api/               → API server and route
  index.ts
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

Use either `node dist/cli/cli.js` or `npx metrics-dashboard` in all CLI commands.

### Generate JSON + HTML
```bash
npx metrics-dashboard tests/fixtures/portfolio --json --html
```

### CLI Console Report
```bash
npx metrics-dashboard tests/fixtures/portfolio --cli
```

### Custom Config (override subsystem weights)
```bash
npx metrics-dashboard tests/fixtures/portfolio --config myconfig.json --json
```

### Start API Server (CLI)
```bash
npx metrics-dashboard --server           # default port 3000
npx metrics-dashboard --server --port 5000  # custom port
```

Custom port:
```bash
npx metrics-dashboard --server --port 5000
```

## API

Start server: 
```bash
npx metrics-dashboard --server
```

Available endpoints:

| Method | Path                               | Description                                               |
| ------ | ---------------------------------- | --------------------------------------------------------- |
| GET    | /api/health                        | Simple health check                                       |
| GET    | /api/dashboard                     | Full portfolio dashboard (reads `tests/fixtures/example`) |
| GET    | /api/multi-project?folder=<folder> | Aggregate metrics from folder                             |
| POST   | /api/aggregate                     | Submit a single service JSON for scoring                  |

> The `/multi-project` API endpoint requires the folder to exist in your host system.
> When running in Docker, mount the folder using `-v "$(pwd)/tests/fixtures:/app/tests/fixtures"`.

Example Curl Commands
```bash
# Health
curl http://localhost:3000/api/health

# Multi-project (folder must exist)
curl "http://localhost:3000/api/multi-project?folder=tests/fixtures/example"

# Aggregate a single JSON file
curl -X POST http://localhost:3000/api/aggregate \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/example/service-a/health-report.json
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

Docker image runs the REST API on port 3000, it currently runs API only.

Build the Docker image:
```bash
docker build -t metrics-dashboard .
```

Run:
```bash
docker run -p 3000:3000 metrics-dashboard
```

> Note: /multi-project API reads local metrics folders. You must mount your fixtures folder inside the container:
```bash
docker run -p 3000:3000 -v "$(pwd)/tests/fixtures:/app/tests/fixtures" metrics-dashboard
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