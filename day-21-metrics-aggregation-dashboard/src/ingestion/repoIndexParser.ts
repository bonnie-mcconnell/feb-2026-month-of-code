import { MetricsParseError } from "./errors"
import { NormalizedRepositoryMetrics } from "../schema/internalTypes"

export function parseRepositoryMetrics(
  raw: unknown
): NormalizedRepositoryMetrics {

  if (typeof raw !== "object" || raw === null) {
    throw new MetricsParseError(
      "repository",
      "Invalid JSON structure"
    )
  }

  const data = raw as Record<string, unknown>

  const loc = data.linesOfCode
  const churn = data.churnScore
  const complexity = data.complexityScore

  if (
    typeof loc !== "number" ||
    typeof churn !== "number" ||
    typeof complexity !== "number"
  ) {
    throw new MetricsParseError(
      "repository",
      "Missing or invalid numeric fields"
    )
  }

  return {
    linesOfCode: loc,
    churnScore: churn,
    complexityScore: complexity,
  }
}