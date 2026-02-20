// src/schema/internalTypes.ts

export interface NormalizedUptimeMetrics {
  averageAvailabilityPct: number
  incidentsLast30Days: number
  longestOutageMinutes: number
}

export interface NormalizedJobMetrics {
  totalProcessed: number
  failureRatePct: number
  retryRatePct: number
  deadLetterRatePct: number
}

export interface NormalizedRepositoryMetrics {
  linesOfCode: number
  churnScore: number
  complexityScore: number
}

export interface NormalizedRepoHealthMetrics {
  healthScore: number
  contributorRiskPct: number
  stalenessDays: number
}