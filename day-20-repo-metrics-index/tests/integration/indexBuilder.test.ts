import path from "node:path"
import { describe, it, expect } from "vitest"
import { buildIndex } from "../../src/indexer/indexBuilder.js"

describe("buildIndex integration", () => {
  it("builds index for fixture repo", async () => {
    const root = path.resolve("tests/fixtures/sample-repo")

    const index = await buildIndex({
      rootPath: root,
      includeExtensions: null,
      parallelism: 2,
      enableGit: false,
      includeBinaryAnalysis: true
    })

    expect(index.files.length).toBeGreaterThan(0)
    expect(Object.keys(index.directories).length).toBeGreaterThan(0)
  })
})