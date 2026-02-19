import { describe, it, expect } from "vitest"
import { aggregateDirectories } from "../../src/metrics/directoryAggregator.js"

describe("directoryAggregator", () => {
  it("aggregates nested directories correctly", () => {
    const map = new Map()

    aggregateDirectories(
      "src/index.ts",
      { total: 10, code: 8, comment: 1, blank: 1 },
      map
    )

    aggregateDirectories(
      "src/utils/helper.ts",
      { total: 5, code: 4, comment: 0, blank: 1 },
      map
    )

    expect(map.get("src")?.totalLines).toBe(15)
    expect(map.get("src/utils")?.totalLines).toBe(5)
  })
})