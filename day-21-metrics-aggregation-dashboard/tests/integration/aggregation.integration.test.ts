import { describe, it, expect } from 'vitest';

import { aggregateMetrics } from "../../src/aggregation/aggregationEngine"

describe("integration: full aggregation", () => {

  it("aggregates all subsystems deterministically", () => {

    const result = aggregateMetrics({
      uptime: {
        averageAvailabilityPct: 99,
        incidentsLast30Days: 3,
        longestOutageMinutes: 10,
      },
      jobs: {
        totalProcessed: 1000,
        failureRatePct: 5,
        retryRatePct: 10,
        deadLetterRatePct: 1,
      },
      repository: {
        linesOfCode: 15000,
        churnScore: 60,
        complexityScore: 70,
      },
      repoHealth: {
        healthScore: 80,
        contributorRiskPct: 30,
        stalenessDays: 5,
      },
      now: () => "2026-01-01T00:00:00.000Z",
    })

    expect(result.system.version).toBe("1.0.0")
    expect(result.overallRiskScore).toBeGreaterThan(0)
    expect(result.overallHealthScore).toBeLessThanOrEqual(100)
  })

})