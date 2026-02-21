#!/usr/bin/env node

import fs from "node:fs"
import { loadMetricsFolder } from "../ingestion/loadMetricsFolder"
import { aggregateMultipleProjects, MultiProjectDashboard } from "../aggregation/multiProjectAggregator"
import { generateHeatmapHtml } from "../reporters/htmlGenerator"
import { renderCliReport } from "../reporters/cliReporter"
import { loadConfigFromFile } from "../config/configLoader"
import { startServer } from "../api/server"
import { DashboardConfig } from "../config/config"

interface CLIArgs {
  folder?: string
  configPath?: string
  json?: boolean
  html?: boolean
  cli?: boolean
  server?: boolean
  port?: number
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
      default:
        if (!parsed.folder) parsed.folder = a
        i++
        break
    }
  }

  return parsed
}

async function main() {
  const args = parseArgs()

  if (!args.folder && !args.server) {
    console.error(
      "Usage: cli <metrics-folder> [--json] [--html] [--cli] [--config <file>] [--server] [--port <number>]"
    )
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
    console.log("dashboard.json generated")
  }

  if (args.html && dashboard) {
    const html = generateHeatmapHtml(dashboard)
    fs.writeFileSync("dashboard.html", html)
    console.log("dashboard.html generated")
  }

  if (args.cli && dashboard) {
    dashboard.projects.forEach((p) =>
      renderCliReport(p.metrics)
    )
  }

  if (args.server) {
    const port = args.port ?? 3000
    startServer(port)
  }
}

main()