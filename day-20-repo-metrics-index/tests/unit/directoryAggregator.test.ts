import { describe, it, expect } from "vitest"
import { aggregateDirectories } from "../../src/metrics/directoryAggregator.js"
import type { DirectoryMetrics } from "../../src/types/metrics.js"

describe("directoryAggregator", () => {
  it("aggregates nested directories correctly", () => {
    const map = new Map<string, DirectoryMetrics>()

    aggregateDirectories(
      "src/index.ts",
      { total: 10, code: 8, comments: 1, blank: 1 },
      map
    )

    aggregateDirectories(
      "src/utils/helper.ts",
      { total: 5, code: 4, comments: 0, blank: 1 },
      map
    )

    expect(map.get("src")?.totalLines).toBe(15)
    expect(map.get("src")?.codeLines).toBe(12)
    expect(map.get("src/utils")?.totalLines).toBe(5)
  })
})