import fs from "node:fs/promises"
import path from "node:path"
import ignorePkg from "ignore"

const ignore = ignorePkg.default ?? ignorePkg

const DEFAULT_IGNORES = [
  ".git",
  "node_modules",
  "dist",
  "build"
]

export async function createIgnoreResolver(rootPath: string) {
  const ig = ignore()

  ig.add(DEFAULT_IGNORES)

  try {
    const gitignorePath = path.join(rootPath, ".gitignore")
    const content = await fs.readFile(gitignorePath, "utf8")
    ig.add(content)
  } catch {
    // .gitignore optional
  }

  return {
    shouldIgnore(relativePath: string): boolean {
      return ig.ignores(relativePath)
    }
  }
}