import fs from "node:fs"
import path from "node:path"

import { parseUptimeMetrics } from "./uptimeParser"
import { parseJobMetrics } from "./jobMetricsParser"
import { parseJobCsv } from "./csvJobParser"
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

  const tryLoadJson = (
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
      throw new MetricsParseError(
        key as string,
        "Invalid JSON structure"
      )
    }
  }

  // -----------------------
  // JSON Sources (preferred)
  // -----------------------

  tryLoadJson("uptime.json", parseUptimeMetrics, "uptime")
  tryLoadJson("repo-index.json", parseRepositoryMetrics, "repository")
  tryLoadJson("health-report.json", parseRepoHealthMetrics, "repoHealth")

  // Jobs: support BOTH JSON and CSV
  const jobsJsonPath = resolve("jobs.json")
  const jobsCsvPath = resolve("jobs.csv")

  if (fs.existsSync(jobsJsonPath)) {

    try {
      const raw = JSON.parse(
        fs.readFileSync(jobsJsonPath, "utf-8")
      )
      result.jobs = parseJobMetrics(raw)
    } catch (err) {
      if (err instanceof MetricsParseError) throw err
      throw new MetricsParseError("jobs", "Invalid jobs.json")
    }

  } else if (fs.existsSync(jobsCsvPath)) {

    const csv = fs.readFileSync(jobsCsvPath, "utf-8")
    result.jobs = parseJobCsv(csv)

  }

  return result
}