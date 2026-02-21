import { MetricsParseError } from "./errors"
import { NormalizedJobMetrics } from "../schema/internalTypes"

export function parseJobMetrics(
  raw: unknown
): NormalizedJobMetrics {

  if (typeof raw !== "object" || raw === null) {
    throw new MetricsParseError(
      "jobs",
      "Invalid JSON structure"
    )
  }

  const data = raw as Record<string, unknown>

  const total = data.totalProcessed
  const failure = data.failureRatePct
  const retry = data.retryRatePct
  const dead = data.deadLetterRatePct

  if (
    typeof total !== "number" ||
    typeof failure !== "number" ||
    typeof retry !== "number" ||
    typeof dead !== "number"
  ) {
    throw new MetricsParseError(
      "jobs",
      "Missing or invalid numeric fields"
    )
  }

  return {
    totalProcessed: total,
    failureRatePct: failure,
    retryRatePct: retry,
    deadLetterRatePct: dead,
  }
}