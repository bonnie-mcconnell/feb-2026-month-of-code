import fs from "node:fs/promises"
import path from "node:path"

export interface DependencyStats {
  internal: number
  external: number
}

export async function analyzeDependencies(
  rootPath: string,
  relativePath: string
): Promise<DependencyStats> {
  const fullPath = path.join(rootPath, relativePath)
  const content = await fs.readFile(fullPath, "utf8")

  const importRegex =
    /import\s+.*?from\s+["'](.+?)["']|require\(["'](.+?)["']\)/g

  let internal = 0
  let external = 0

  let match
  while ((match = importRegex.exec(content))) {
    const dep = match[1] || match[2]

    if (dep.startsWith("."))
      internal++
    else
      external++
  }

  return { internal, external }
}