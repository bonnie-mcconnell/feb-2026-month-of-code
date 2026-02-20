import fs from "node:fs/promises"
import path from "node:path"
import { createIgnoreResolver } from "./ignoreResolver.js"

export async function* walkFiles(rootPath: string): AsyncGenerator<string> {
  const resolver = await createIgnoreResolver(rootPath)

  async function* walkDir(currentPath: string): AsyncGenerator<string> {
    const entries = await fs.readdir(currentPath, { withFileTypes: true })

    entries.sort((a, b) => a.name.localeCompare(b.name))

    for (const entry of entries) {
      if (entry.name.startsWith(".")) continue

      const fullPath = path.join(currentPath, entry.name)

      const relativePath = path
        .relative(rootPath, fullPath)
        .split(path.sep)
        .join("/")

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