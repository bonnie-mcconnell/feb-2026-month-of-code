import { describe, it, expect } from 'vitest';
import {
  evaluateJobRisk,
  evaluateRepositoryRisk,
  computeCrossSignalBoost,
  computeOverallRisk,
} from "../../src/aggregation/riskEvaluator"

describe("riskEvaluator", () => {

  it("calculates job risk deterministically", () => {
    const result = evaluateJobRisk({
      totalProcessed: 1000,
      failureRatePct: 10,
      retryRatePct: 20,
      deadLetterRatePct: 5,
    })

    expect(result.jobRisk).toBeCloseTo(
      10 * 0.6 + 20 * 0.3 + 5 * 0.1
    )
  })

  it("calculates repository risk correctly", () => {
    const result = evaluateRepositoryRisk({
      linesOfCode: 5000,
      churnScore: 50,
      complexityScore: 80,
    })

    expect(result.repoRisk).toBeCloseTo(
      80 * 0.6 + 50 * 0.4
    )
  })

  it("applies cross-signal boost", () => {
    const boost = computeCrossSignalBoost({
      repository: {
        linesOfCode: 10000,
        churnScore: 80,
        complexityScore: 75,
      },
      jobs: {
        totalProcessed: 1000,
        failureRatePct: 12,
        retryRatePct: 25,
        deadLetterRatePct: 2,
      },
    })

    expect(boost).toBe(20)
  })

  it("rebalances weights when subsystems missing", () => {
    const result = computeOverallRisk({
      uptimeRisk: 20,
      jobRisk: undefined,
      repoRisk: 40,
      healthRisk: undefined,
      crossSignalBoost: 0,
    })

    expect(result.overallRiskScore).toBeGreaterThan(0)
    expect(result.overallRiskScore).toBeLessThanOrEqual(100)
  })

})