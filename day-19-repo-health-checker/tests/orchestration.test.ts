import { describe, it, expect } from "vitest"
import { analyzeRepository } from "../src/index.js"

class MockClient {
  async request(path: string) {
    if (path.includes("commits"))
      return [{ commit: { author: { date: new Date().toISOString() } } }]
    if (path.includes("contributors"))
      return [{ login: "user", contributions: 10 }]
    if (path.includes("issues"))
      return []
    if (path.includes("pulls"))
      return []
    if (path.includes("releases"))
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
