import { describe, it, expect } from "vitest"
import path from "node:path"
import { calculateLOC } from "../../src/metrics/localCalculator.js"

describe("locCalculator", () => {
  it("correctly counts code, blank, and comments", async () => {
    const root = path.resolve("tests/fixtures")
    const result = await calculateLOC(root, "loc-sample.ts")

    expect(result.total).toBe(6)
    expect(result.comment).toBe(1)
    expect(result.blank).toBe(1)
    expect(result.code).toBe(4)
  })
})