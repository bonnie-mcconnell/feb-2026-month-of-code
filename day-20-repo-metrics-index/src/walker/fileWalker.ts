import fs from "node:fs/promises"
import path from "node:path"
import { createIgnoreResolver } from "./ignoreResolver.js"

export async function* walkFiles(rootPath: string) {
  const resolver = await createIgnoreResolver(rootPath)

  async function* walkDir(currentPath: string) {
    const entries = await fs.readdir(currentPath, { withFileTypes: true })

    // Deterministic ordering
    entries.sort((a, b) => a.name.localeCompare(b.name))

    for (const entry of entries) {
      const fullPath = path.join(currentPath, entry.name)
      const relativePath = path.relative(rootPath, fullPath)

      if (resolver.shouldIgnore(relativePath)) continue

      if (entry.isDirectory()) {
        yield* walkDir(fullPath)
      } else if (entry.isFile()) {
        yield relativePath
      }
    }
  }

  yield* walkDir(rootPath)
}