import { describe, it, expect } from "vitest"
import { analyzeRepository } from "../src/index.js"

class MockClient {
  callCount = 0

  async request(path: string) {
    this.callCount++

    if (this.callCount > 1) return []

    if (path.includes("commits"))
      return [{ commit: { author: { date: new Date().toISOString() } } }]

    if (path.includes("contributors"))
      return [{ login: "user", contributions: 10 }]

    if (path.includes("issues"))
      return []

    if (path.includes("pulls"))
      return []

    return []
  }
}


describe("orchestration", () => {
  it("produces a health report", async () => {
    const report = await analyzeRepository(
      { owner: "x", repo: "y" },
      new MockClient() as any
    )

    expect(report.overallScore).toBeGreaterThanOrEqual(0)
  })
})
