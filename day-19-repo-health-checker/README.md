# Repo Health Checker

Analyze GitHub repository health and risk using a weighted, rule-based metric system.  
Ideal for engineering teams, maintainers, or portfolio showcases.

---

## Features

- Weighted metrics for overall health score
- GraphQL + REST GitHub API support
- Historical trend analysis
- Compare multiple repositories
- Type-safe, strict TypeScript codebase
- JSON Schema validation of reports
- CLI outputs: table or JSON
- Appendable, testable, and fully automatable

---

## Install & Build

```bash
npm install
npm run build
```

## Local Development/CLI Testing

Link the CLI globally to test without installing:

```bash
npm link
repo-health facebook/react --format table --token $GITHUB_TOKEN
```

> Note: In PowerShell, reference environment variables as `$env:GITHUB_TOKEN

## CLI Usage
```bash
repo-health owner/repo               # Basic analysis
repo-health owner/repo --json        # Output JSON
repo-health owner/repo --format table  # Output table
repo-health owner/repo --graphql --token YOUR_TOKEN
repo-health owner/repo --trend 6 --token $GITHUB_TOKEN    # Historical trend mode
repo-health compare ownerA/repoA ownerB/repoB
repo-health schema                    # Print JSON schema
```

## CLI Options

| Option                 | Description                   |               |
| ---------------------- | ----------------------------- | ------------- |
| `--json`               | Output JSON                   |               |
| `--format <table       | json>`                        | Output format |
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
repo-health facebook/react --format table

# Compare React and Vue
repo-health compare facebook/react vuejs/vue

# Print schema
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
  - Token missing or invalid
- Always pass `--token YOUR_TOKEN` for popular or private repos.


CI Badge

![CI](https://github.com/BonnieProsper/feb-2026-month-of-code/day-19-repo-health-checker/actions/workflows/ci.yml/badge.svg)

License

MIT

