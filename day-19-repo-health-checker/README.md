# Repo Health Checker

Analyze GitHub repository health using weighted metrics.

## Features

- REST + GraphQL modes
- Historical trend mode
- Repo comparison
- JSON Schema validation
- CLI output (table/json)
- Type-safe GitHub SDK
- Strict TypeScript

## Install

```bash
npm install
npm run build
Usage
repo-health owner/repo
repo-health owner/repo --json
repo-health owner/repo --graphql --token YOUR_TOKEN
repo-health compare ownerA/repoA ownerB/repoB
repo-health owner/repo --trend 6
GraphQL Mode
Requires GitHub token:

repo-health vercel/next.js --graphql --token $GITHUB_TOKEN
Exit Codes
0 = healthy

1 = failed threshold or error

License
MIT

Coverage badge

![CI](https://github.com/BonnieProsper/feb-2026-month-of-code/day-19-repo-health-checker/actions/workflows/ci.yml/badge.svg)
