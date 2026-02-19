import { describe, it, expect } from "vitest"
import path from "node:path"
import { walkFiles } from "../../src/walker/fileWalker.js"

const FIXTURE = path.resolve("tests/fixtures/simple-repo")

describe("fileWalker", () => {
  it("walks files deterministically and respects ignores", async () => {
    const files: string[] = []

    for await (const file of walkFiles(FIXTURE)) {
      files.push(file)
    }

    expect(files).toEqual([
      "README.md",
      "src/index.ts",
      "src/util.ts"
    ])
  })
})