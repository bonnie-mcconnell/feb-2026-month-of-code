# SecretScanner

A fast, deterministic secret detection engine for Node.js projects.

SecretScanner scans your repository for exposed credentials, API keys, tokens, and high-entropy secrets using a structured rule engine with severity scoring and stable, reproducible output.

Designed for CI enforcement and reproducible results.

## Features

- Pattern-based secret detection (API keys, tokens, private keys, etc)
- Entropy-based secret detection
- Severity scoring: LOW / MEDIUM / HIGH / CRITICAL
- Deterministic stable sorting
- Duplicate finding elimination
- .gitignore & .secretscannerignore support
- ESM-native (NodeNext)
- CI-friendly exit codes (0 clean, 1 secrets found)
- JSON and console reporters
- Zero external runtime dependencies (except ignore)

## Installation
```bash
npm install
npm run build
```

## Usage

Scan a directory:
```bash
node dist/index.js scan .
```

With custom entropy settings:
```bash
node dist/index.js scan . --entropy-threshold 4.8 --min-entropy-length 24
```

Console output example:
```yaml
[HIGH] AWS_ACCESS_KEY
  File: src/config.ts
  Line: 12
  Description: Possible AWS access key detected
  Snippet: AKIAIOSFODNN7EXAMPLE

Severity Summary:
  CRITICAL: 1
  HIGH: 2
  MEDIUM: 0
  LOW: 1

Found 4 potential secrets.
```

JSON output:
```bash
node dist/index.js scan . --reporter json
```
```json
[
  {
    "ruleId": "AWS_ACCESS_KEY",
    "severity": "HIGH",
    "filePath": "src/config.ts",
    "lineNumber": 12,
    "description": "Possible AWS access key detected",
    "snippet": "AKIAIOSFODNN7EXAMPLE",
    "entropyScore": 4.91
  }
]
```

Quiet mode (no console output, exit code still correct):
```bash
node dist/index.js scan . --quiet
```

Show version:
```bash
node dist/index.js --version
```

## Ignore Files

SecretScanner respects:
- Built-in ignores:
```
node_modules/
dist/
build/
.git/
```
- .gitignore and .secretscannerignore
- Example .secretscannerignore:
```
tests/**
fixtures/**
```

## Severity Model
Severity Meaning
CRITICAL: Highly likely production credential
HIGH: Strong credential pattern match
MEDIUM: Suspicious token or structured secret
LOW: Entropy-only match

Findings are deduplicated, stable-sorted, and deterministic across runs.

## CI Integration

SecretScanner exits with code 1 if secrets are found.

You can add this as a GitHub Actions workflow by creating
`.github/workflows/scan-secrets.yml`:

```yaml
name: SecretScanner

on:
  push:
    branches:
      - main
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - run: node dist/index.js scan .
```

## Testing
```bash
npm run test
```

Includes:
- Integration tests
- CI failure simulation
- ESM compatibility tests
- Ignore file validation

## Architecture
```
cli/
reporters/
rules/
scanner/
utils/
types/
index.ts
tests/ and fixtures/
```

Core pipeline:
- File walker (async generator)
- Pattern engine
- Entropy engine
- Deduplication
- Stable sort
- Reporter
- CI exit code enforcement

## Design Principles

- Deterministic output
- No false-positive amplification
- CI-first
- Minimal surface area
- Reproducible scanning

## Version 1 Scope

- Built-in rules only
- No plugin system
- No autofix
- No baseline file support

## Future Additions

- Custom rule loading
- SARIF output
- Pre-commit hook integration
- Config file support (.secretscanner.json)
- Rule packs

## License

MIT