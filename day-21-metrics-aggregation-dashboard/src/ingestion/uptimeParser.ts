import { MetricsParseError } from "./errors"
import { NormalizedUptimeMetrics } from "../schema/internalTypes"

export function parseUptimeMetrics(
  raw: unknown
): NormalizedUptimeMetrics {

  if (typeof raw !== "object" || raw === null) {
    throw new MetricsParseError(
      "uptime",
      "Invalid JSON structure"
    )
  }

  const data = raw as Record<string, unknown>

  const avg = data.averageAvailabilityPct
  const incidents = data.incidentsLast30Days
  const outage = data.longestOutageMinutes

  if (
    typeof avg !== "number" ||
    typeof incidents !== "number" ||
    typeof outage !== "number"
  ) {
    throw new MetricsParseError(
      "uptime",
      "Missing or invalid numeric fields"
    )
  }

  return {
    averageAvailabilityPct: avg,
    incidentsLast30Days: incidents,
    longestOutageMinutes: outage,
  }
}