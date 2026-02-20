import { walkFiles } from "../walker/fileWalker.js"
import { analyzeFile } from "../metrics/fileMetrics.js"
import { aggregateDirectories } from "../metrics/directoryAggregator.js"
import type { DirectoryMetrics } from "../types/metrics.js"

export interface RepoIndex {
  files: Awaited<ReturnType<typeof analyzeFile>>[]
  directories: Record<string, DirectoryMetrics>
}

export async function buildIndex(rootPath: string): Promise<RepoIndex> {
  const files = []
  const directoryMap = new Map<string, DirectoryMetrics>()

  for await (const relativePath of walkFiles(rootPath)) {
    const fileMetrics = await analyzeFile(rootPath, relativePath)
    if (!fileMetrics) continue

    files.push(fileMetrics)

    aggregateDirectories(
      relativePath,
      fileMetrics.loc,
      directoryMap
    )
  }

  const directories = Object.fromEntries(directoryMap)

  return {
    files,
    directories
  }
}