import fs from "node:fs"
import path from "node:path"

import { parseUptimeMetrics } from "./uptimeParser"
import { parseJobMetrics } from "./jobMetricsParser"
import { parseRepositoryMetrics } from "./repoIndexParser"
import { parseRepoHealthMetrics } from "./healthReportParser"
import { MetricsParseError } from "./errors"

import { AggregationInput } from "../aggregation/aggregationEngine"

export interface LoadMetricsOptions {
  folderPath: string
}

function safeReadJson(filePath: string): unknown {
  const raw = fs.readFileSync(filePath, "utf-8")
  return JSON.parse(raw)
}

export function loadMetricsFolder(
  options: LoadMetricsOptions
): AggregationInput {

  const { folderPath } = options

  if (!fs.existsSync(folderPath)) {
    throw new Error(`Metrics folder does not exist: ${folderPath}`)
  }

  const resolve = (filename: string) =>
    path.join(folderPath, filename)

  const result: AggregationInput = {}

  // -------------------------
  // uptime.json
  // -------------------------
  const uptimePath = resolve("uptime.json")
  if (fs.existsSync(uptimePath)) {
    try {
      const raw = safeReadJson(uptimePath)
      result.uptime = parseUptimeMetrics(raw)
    } catch (err) {
      if (err instanceof MetricsParseError) {
        throw err
      }
      throw new MetricsParseError(
        "uptime",
        "Invalid JSON format"
      )
    }
  }

  // -------------------------
  // jobs.json
  // -------------------------
  const jobsPath = resolve("jobs.json")
  if (fs.existsSync(jobsPath)) {
    try {
      const raw = safeReadJson(jobsPath)
      result.jobs = parseJobMetrics(raw)
    } catch (err) {
      if (err instanceof MetricsParseError) {
        throw err
      }
      throw new MetricsParseError(
        "jobs",
        "Invalid JSON format"
      )
    }
  }

  // -------------------------
  // repo-index.json
  // -------------------------
  const repoPath = resolve("repo-index.json")
  if (fs.existsSync(repoPath)) {
    try {
      const raw = safeReadJson(repoPath)
      result.repository = parseRepositoryMetrics(raw)
    } catch (err) {
      if (err instanceof MetricsParseError) {
        throw err
      }
      throw new MetricsParseError(
        "repository",
        "Invalid JSON format"
      )
    }
  }

  // -------------------------
  // health-report.json
  // -------------------------
  const healthPath = resolve("health-report.json")
  if (fs.existsSync(healthPath)) {
    try {
      const raw = safeReadJson(healthPath)
      result.repoHealth = parseRepoHealthMetrics(raw)
    } catch (err) {
      if (err instanceof MetricsParseError) {
        throw err
      }
      throw new MetricsParseError(
        "repoHealth",
        "Invalid JSON format"
      )
    }
  }

  return result
}