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

JSON reporter:
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

Example GitHub Action:
```yaml
- name: Scan for secrets
  run: node dist/index.js scan .
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