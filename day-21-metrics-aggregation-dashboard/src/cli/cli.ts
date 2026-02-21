#!/usr/bin/env node

import fs from "fs"
import path from "path"
import { aggregateMetrics } from "../aggregation/aggregationEngine"
import { renderCliReport } from "../reporters/cliReporter"
import { generateJsonReport } from "../reporters/jsonReporter"
import { generateHtmlReport } from "../reporters/htmlGenerator"

import {
  NormalizedUptimeMetrics,
  NormalizedJobMetrics,
  NormalizedRepositoryMetrics,
  NormalizedRepoHealthMetrics,
} from "../schema/internalTypes"

interface CliInput {
  uptime?: NormalizedUptimeMetrics
  jobs?: NormalizedJobMetrics
  repository?: NormalizedRepositoryMetrics
  repoHealth?: NormalizedRepoHealthMetrics
}

function loadInput(filePath: string): CliInput {
  const raw = fs.readFileSync(path.resolve(filePath), "utf-8")
  return JSON.parse(raw)
}

async function main() {
  const inputPath = process.argv[2]

  if (!inputPath) {
    console.error("Usage: cli <input.json>")
    process.exit(1)
  }

  const input = loadInput(inputPath)

  const unified = aggregateMetrics(input)

  renderCliReport(unified)

  const json = generateJsonReport(unified)
  fs.writeFileSync("report.json", JSON.stringify(json, null, 2))

  const html = generateHtmlReport(unified)
  fs.writeFileSync("report.html", html)
}

main()