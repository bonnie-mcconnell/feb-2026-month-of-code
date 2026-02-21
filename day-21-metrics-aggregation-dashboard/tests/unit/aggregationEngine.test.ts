import { describe, it, expect } from 'vitest';
import { aggregateMetrics } from "../../src/aggregation/aggregationEngine"

describe("aggregationEngine", () => {

  it("produces deterministic output with injected clock", () => {

    const result = aggregateMetrics({
      uptime: {
        averageAvailabilityPct: 99.9,
        incidentsLast30Days: 1,
        longestOutageMinutes: 5,
      },
      now: () => "2026-01-01T00:00:00.000Z",
    })

    expect(result.system.generatedAt).toBe(
      "2026-01-01T00:00:00.000Z"
    )

    expect(result.system.sources.uptime).toBe(true)
  })

})