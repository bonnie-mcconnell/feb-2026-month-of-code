#!/usr/bin/env node

import fs from "node:fs"
import { loadMetricsFolder } from "../ingestion/loadMetricsFolder.js"
import {
  aggregateMultipleProjects,
  MultiProjectDashboard,
} from "../aggregation/multiProjectAggregator.js"
import { generateHeatmapHtml } from "../reporters/htmlGenerator.js"
import { renderCliReport } from "../reporters/cliReporter.js"
import { loadConfigFromFile } from "../config/configLoader.js"
import { startServer } from "../api/server.js"
import { DashboardConfig } from "../config/config.js"

interface CLIArgs {
  folder?: string
  configPath?: string
  json?: boolean
  html?: boolean
  cli?: boolean
  server?: boolean
  port?: number
}

function printUsage(): void {
  console.log(`
Metrics Aggregation Dashboard

Usage:
  metrics-dashboard <metrics-folder> [options]

Options:
  --json                 Generate dashboard.json
  --html                 Generate dashboard.html
  --cli                  Print console report
  --config <file>        Custom weight configuration
  --server               Start REST API server
  --port <number>        Custom server port (default: 3000)
`)
}

function parseArgs(): CLIArgs {
  const args = process.argv.slice(2)
  const parsed: CLIArgs = {}

  let i = 0
  while (i < args.length) {
    const a = args[i]

    switch (a) {
      case "--config":
        parsed.configPath = args[i + 1]
        i += 2
        break
      case "--json":
        parsed.json = true
        i++
        break
      case "--html":
        parsed.html = true
        i++
        break
      case "--cli":
        parsed.cli = true
        i++
        break
      case "--server":
        parsed.server = true
        i++
        break
      case "--port":
        parsed.port = Number(args[i + 1])
        i += 2
        break
      case "--help":
      case "-h":
        printUsage()
        process.exit(0)
      default:
        if (!parsed.folder) parsed.folder = a
        i++
        break
    }
  }

  return parsed
}

function formatNumber(n: number): string {
  return n.toFixed(2)
}

async function main() {
  const args = parseArgs()

  if (!args.folder && !args.server) {
    printUsage()
    process.exit(1)
  }

  let config: DashboardConfig | undefined
  if (args.configPath) {
    config = loadConfigFromFile(args.configPath)
  }

  let dashboard: MultiProjectDashboard | undefined

  if (args.folder) {
    const bundles = loadMetricsFolder(args.folder)
    dashboard = aggregateMultipleProjects(bundles, config)
  }

  if (args.json && dashboard) {
    fs.writeFileSync(
      "dashboard.json",
      JSON.stringify(dashboard, null, 2)
    )
    console.log("✔ dashboard.json generated")
  }

  if (args.html && dashboard) {
    const html = generateHeatmapHtml(dashboard)
    fs.writeFileSync("dashboard.html", html)
    console.log("✔ dashboard.html generated")
  }

  if (args.cli && dashboard) {
    dashboard.projects.forEach((project) => {
      console.log("\n======================================")
      console.log(`Project: ${project.projectName}`)
      console.log("======================================\n")

      renderCliReport(project.metrics)
    })
  }

  if (args.server) {
    const port = args.port ?? 3000
    startServer(port)
  }
}

main()