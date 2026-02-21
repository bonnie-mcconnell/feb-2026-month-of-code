#!/usr/bin/env node

import fs from "node:fs"
import { loadMetricsFolder } from "../ingestion/loadMetricsFolder"
import { aggregateMultipleProjects } from "../aggregation/multiProjectAggregator"
import { generateHeatmapHtml } from "../reporters/htmlGenerator"

async function main() {

  const folder = process.argv[2]

  if (!folder) {
    console.error("Usage: cli <metrics-folder>")
    process.exit(1)
  }

  const bundles = loadMetricsFolder(folder)
  const dashboard = aggregateMultipleProjects(bundles)

  fs.writeFileSync(
    "dashboard.json",
    JSON.stringify(dashboard, null, 2)
  )

  const html = generateHeatmapHtml(dashboard)
  fs.writeFileSync("dashboard.html", html)

  console.log("Portfolio dashboard generated.")
}

main()