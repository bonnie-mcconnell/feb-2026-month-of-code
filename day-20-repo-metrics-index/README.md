## Repo Metrics Index

![CI](https://img.shields.io/github/actions/workflow/status/BronsonPieper/feb-2026-month-of-code/nodejs.yml?branch=main&label=CI&logo=github)

A Node.js CLI for generating structural metrics for local repositories.

Produces deterministic JSON containing per-file and directory-level insights including LOC breakdown, complexity estimation, dependency counts, and optional Git churn.

Built for performance, parallelism, and clean architectural separation.

## Capabilities

- Line-of-code analysis (total/code/comment/blank)
- Cyclomatic complexity estimation
- Internal vs external dependency counting
- Directory-level metric aggregation
- Optional Git churn integration
- Parallel file processing
- Extension filtering
- Binary file detection
- Schema-validated JSON output
- Cross-platform path normalization

## Installation

Node 18+ recommended.
```bash
npm install
npm run build
```

## Usage
```bash
node dist/cli/cli.js <repository-root> [options]
```

## Examples

Analyze current directory:
```bash
node dist/cli/cli.js .
```

Analyze another project with filters:
```bash
node dist/cli/cli.js ../some-project --extensions ts,js --parallel 8
```

Write output to file:
```bash
node dist/cli/cli.js . --no-git -o metrics.json
```

Write pretty output to file:
```bash
node dist/cli/cli.js . --format pretty -o metrics.json --no-git
```

## CLI Options

| Option                | Description                       |
| --------------------- | --------------------------------- |
| `--extensions ts,js`  | Only include specific file types  |
| `--parallel <n>`      | Number of concurrent file workers |
| `--no-git`            | Disable Git churn analysis        |
| `--skip-binary`       | Skip binary detection             |
| `-o, --output <file>` | Write JSON output to file                                               | `--format <type>`     |    Output format: `json` (default) or `pretty`   |

## Output Structure

Produces a validated JSON document containing:
- Repository metadata
- Per-file metrics
  - LOC breakdown
  - Complexity score
  - Dependency counts
  - Optional churn
- Directory aggregation (LOC + dependency totals)
- Aggregate totals

Validation enforced via Zod schema before output.

## Architecture

```
walker/        Recursive file traversal
metrics/       LOC, complexity, dependency, churn analysis
git/           Git integration layer
indexer/       Orchestration & aggregation (`indexBuilder`)
reporters/     Output formatting
cli/           Argument parsing
types/         Shared contracts
config/        Runtime configuration
utils/         Helpers
```

Separation of concerns is strict: traversal, metric extraction, and reporting are fully decoupled.

## Development

Run tests:
```bash
npm test
```

Build:
```bash
npm run build
```
## Design Principles

- Deterministic output
- Parallelized processing with bounded concurrency (`promisePool`)
- Streaming-friendly file handling
- Strong TypeScript typing
- Extensible metric pipeline
- Minimal runtime dependencies

## Benchmark

Environment: Mac M1, 8GB RAM

- Projects scanned: 37
- Files processed: 612
- Runtime (no git): ~1.2s
- Runtime (with git): ~3.8s
- Peak memory: ~75MB

Example Output

See example-output.json