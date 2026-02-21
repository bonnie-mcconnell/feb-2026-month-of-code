import fs from "node:fs"
import path from "node:path"

import { parseUptimeMetrics } from "./uptimeParser"
import { parseJobMetrics } from "./jobMetricsParser"
import { parseRepositoryMetrics } from "./repoIndexParser"
import { parseRepoHealthMetrics } from "./healthReportParser"
import { MetricsParseError } from "./errors"

import { AggregationInput } from "../aggregation/aggregationEngine"

export function loadSingleProjectMetrics(
  folderPath: string
): AggregationInput {

  if (!fs.existsSync(folderPath)) {
    throw new Error(`Metrics folder does not exist: ${folderPath}`)
  }

  const resolve = (filename: string) =>
    path.join(folderPath, filename)

  const result: AggregationInput = {}

  const tryLoad = (
    filename: string,
    parser: (raw: unknown) => any,
    key: keyof AggregationInput
  ) => {
    const filePath = resolve(filename)
    if (!fs.existsSync(filePath)) return

    try {
      const raw = JSON.parse(
        fs.readFileSync(filePath, "utf-8")
      )
      result[key] = parser(raw)
    } catch (err) {
      if (err instanceof MetricsParseError) throw err
      throw new MetricsParseError(key as string, "Invalid JSON")
    }
  }

  tryLoad("uptime.json", parseUptimeMetrics, "uptime")
  tryLoad("jobs.json", parseJobMetrics, "jobs")
  tryLoad("repo-index.json", parseRepositoryMetrics, "repository")
  tryLoad("health-report.json", parseRepoHealthMetrics, "repoHealth")

  return result
}