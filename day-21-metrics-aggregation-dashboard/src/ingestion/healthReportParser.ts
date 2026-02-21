import { MetricsParseError } from "./errors"
import { NormalizedRepoHealthMetrics } from "../schema/internalTypes"

export function parseRepoHealthMetrics(
  raw: unknown
): NormalizedRepoHealthMetrics {

  if (typeof raw !== "object" || raw === null) {
    throw new MetricsParseError(
      "repoHealth",
      "Invalid JSON structure"
    )
  }

  const data = raw as Record<string, unknown>

  const healthScore = data.healthScore
  const contributorRisk = data.contributorRiskPct
  const staleness = data.stalenessDays

  if (
    typeof healthScore !== "number" ||
    typeof contributorRisk !== "number" ||
    typeof staleness !== "number"
  ) {
    throw new MetricsParseError(
      "repoHealth",
      "Missing or invalid numeric fields"
    )
  }

  return {
    healthScore,
    contributorRiskPct: contributorRisk,
    stalenessDays: staleness,
  }
}