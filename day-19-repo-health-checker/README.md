# Repo Health Checker

Analyze GitHub repository health and risk using a weighted, rule-based metric system.  
Ideal for engineering teams, maintainers, or portfolio showcases.

This project provides a CLI and TypeScript library for assessing repository health, including commit activity, contribution distribution, issue/PR hygiene, and staleness. Outputs are validated via JSON Schema and can be exported in multiple formats.

---

## Key Features

- Weighted metrics for overall health score and detailed sub-metrics
- REST & GraphQL GitHub API support
- Historical trend analysis (--trend <months>) to track repo health over time
- Compare multiple repositories side-by-side
- Fully type-safe, strict TypeScript codebase
- JSON Schema validation of all reports
- CLI outputs: table or JSON
- Testable, automatable, and appendable (integration-friendly)
- Configurable via custom weights, commit windows, and caching
- Supports both public and private repositories (via GitHub token)

## Future Enhancements/Limitations

- Large repositories (e.g, facebook/react) may take several minutes or hit GitHub API limits.
  - Mitigations: --window <days>, trend analysis on smaller repos, or caching.
- Rate limits: Make sure to use a valid GitHub token, especially for GraphQL or popular repos.

Planned improvements:
- Async batching for commits/issues to speed up large repo analysis
- Optional GitHub App integration for enterprise usage
- Additional metrics for CI/CD pipelines, security scans, and dependency freshness

## Install & Build
```bash
npm install
npm run build
```

For development:
```bash
npm run dev           # Run CLI with ts-node
npm run test          # Run full test suite
npm run lint          # Lint codebase
npm run clean         # Clean build output
```
## Local Development/CLI Testing

Link the CLI globally for local testing:
```bash
npm link
repo-health facebook/react --format table --token $GITHUB_TOKEN
```

> Note: In PowerShell, reference environment variables as `$env:GITHUB_TOKEN

## CLI Usage
```bash
repo-health owner/repo                       # Basic analysis
repo-health owner/repo --json                # JSON output
repo-health owner/repo --format table        # Human-readable table
repo-health owner/repo --graphql --token YOUR_TOKEN
repo-health owner/repo --trend 6 --token $GITHUB_TOKEN
repo-health owner/repo --window 90           # Limit commits to last 90 days
repo-health owner/repo --weights '{"commitActivity":1.5}' # Custom scoring weights
repo-health compare ownerA/repoA ownerB/repoB
repo-health schema                            # Print JSON schema
```

## CLI Options

| Option                 | Description                   |               |
| ---------------------- | ----------------------------- | ------------- |
| `--json`               | Output JSON                   |               |
| `--format table'       | Output human readable table`                        | Or: `--format json'       | Output json                        | Output format |
| `--min-score <number>` | Fail if score below threshold |               |
| `--token <token>`      | GitHub API token              |               |
| `--window <days>`      | Commit window in days         |               |
| `--weights <json>`     | Custom scoring weights        |               |
| `--trend <months>`     | Historical trend mode         |               |
| `--graphql`            | Use GraphQL API               |               |
| `--no-cache`           | Disable caching               |               |
| `--output <file>`      | Write output to file          |               |
| `--schema-file <file>` | Write JSON schema to file     |               |


## GraphQL Mode

Requires GitHub token:
```bash
repo-health vercel/next.js --graphql --token $GITHUB_TOKEN
```
> Supports fetching detailed contributor metrics and PR data more efficiently than REST.

## Compare Mode
```bash
repo-health compare ownerA/repoA ownerB/repoB --token $GITHUB_TOKEN
```

- Outputs JSON object with overall scores of both repositories.
- Useful for benchmarking project health across teams or frameworks.

## Schema Mode
```bash
repo-health schema
```

- Outputs full JSON Schema (repo-health.schema.json) used to validate all reports.
- Supports --schema-file <file> to write schema to a custom location.

## Trend Mode
```bash
repo-health owner/repo --trend 6 --token $GITHUB_TOKEN
```

- Generates historical scores for the last 6 months.
- Large repos may take minutes per month if caching is disabled.
- Use --window <days> to reduce load.

## Exit Codes

- 0 = healthy/success
- 1 = failed threshold or error

## Testing/Manual Validation

Run full test suite:
```bash
npm run test
```

Test CLI commands:
```bash
# Analyze React repo
repo-health facebook/react --format table --token $GITHUB_TOKEN

# Compare React and Vue
repo-health compare facebook/react vuejs/vue --token $GITHUB_TOKEN

# Print JSON schema
repo-health schema
```

Verify schema copied:
```bash
ls dist/schema/repo-health.schema.json
```

Confirm trend mode:
```bash
repo-health facebook/react --trend 6 --token $GITHUB_TOKEN
```

All commands should return without errors.

## Troubleshooting

- GitHub API 422 errors usually mean:
  - Repository not found
  - Github token missing or invalid
- Large repositories may cause timeout or empty output.
- Recommended mitigations:
  - Use --window to limit commits
  - Use caching for repeated runs
  - Use smaller repositories for CI/testing
- Always pass `--token YOUR_TOKEN` for popular or private repos.


# Notes on Large Repositories

Analyzing very large repositories (like facebook/react) may take several minutes or fail/return partial data with GitHub API errors/due to API limits. It may also cause high memory usage in local machines.
To reduce load, consider:
- Using `--window <days>` to limit commit history.
- Using a valid GitHub token with sufficient rate limits.
- Running trend analysis on smaller repositories.
- caching intermediate results


CI Badge

![CI](https://github.com/BonnieProsper/feb-2026-month-of-code/day-19-repo-health-checker/actions/workflows/ci.yml/badge.svg)

License

MIT

