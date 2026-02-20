Repo Metrics Index

A CLI tool for generating structural, complexity, and churn metrics for local repositories.

Designed for performance, extensibility, and clean architecture.

Features

Line of Code (LOC) analysis

Code / Comment / Blank breakdown

Cyclomatic complexity estimation

Directory-level aggregation

Git churn integration (optional)

Parallel file processing

Extension filtering

Schema-validated JSON output

Cross-platform path handling

Installation
npm install
npm run build
Usage
node dist/cli/cli.js <path>

Example:

node dist/cli/cli.js .
node dist/cli/cli.js ../some-project --extensions ts,js --parallel 8
CLI Options
Option	Description
--extensions ts,js	Only include specific file types
--parallel <n>	Number of concurrent file workers
--no-git	Disable Git churn analysis
--skip-binary	Skip binary detection
Output

Produces a validated JSON index containing:

Repository metadata

Per-file metrics

Directory aggregation

Optional churn metrics

Schema enforced with Zod.

Architecture
walker/        file traversal
metrics/       LOC, complexity, churn
git/           Git execution layer
indexer/       orchestration
reporters/     output formatting
cli/           argument parsing
types/         shared contracts
config/        runtime configuration
utils/         helpers
Development

Run tests:

npm test

Build:

npm run build
Design Goals

Stream-based processing for scalability

Deterministic output

Separation of concerns

Minimal runtime dependencies

Extensible metric pipeline


Benchmark (Mac M1, 8GB RAM)
--------------------------------
Repo size: 37 projects
Files scanned: 612
Runtime (no git): 1.2s
Runtime (with git): 3.8s
Peak memory: ~75MB