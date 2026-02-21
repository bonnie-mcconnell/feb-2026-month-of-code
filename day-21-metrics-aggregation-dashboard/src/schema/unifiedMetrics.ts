export const UNIFIED_METRICS_VERSION = "1.0.0" as const

export type UnifiedMetricsVersion = typeof UNIFIED_METRICS_VERSION

export interface UnifiedMetricsV1 {
  system: {
    version: UnifiedMetricsVersion
    generatedAt: string // ISO timestamp
    sources: {
      uptime: boolean
      jobs: boolean
      repository: boolean
      repoHealth: boolean
    }
    riskTier: "LOW" | "MEDIUM" | "HIGH"
  }

  uptime?: {
    averageAvailabilityPct: number        // 0–100
    incidentsLast30Days: number
    longestOutageMinutes: number
    uptimeScore: number                  // 0–100
  }

  jobs?: {
    totalProcessed: number
    failureRatePct: number               // 0–100
    retryRatePct: number                 // 0–100
    deadLetterRatePct: number            // 0–100
    jobReliabilityScore: number          // 0–100
  }

  repository?: {
    linesOfCode: number
    churnScore: number                   // 0–100
    complexityScore: number              // 0–100
    maintainabilityScore: number         // 0–100
  }

  repoHealth?: {
    healthScore: number                  // 0–100
    contributorRiskPct: number           // 0–100
    stalenessDays: number
    activityScore: number                // 0–100
  }

  overallRiskScore: number               // 0–100
  overallHealthScore: number             // 0–100
}