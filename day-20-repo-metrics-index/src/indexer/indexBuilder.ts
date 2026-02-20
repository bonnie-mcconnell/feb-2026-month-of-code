import path from "node:path"
import { walkFiles } from "../walker/fileWalker.js"
import { analyzeFile, type FileMetricsResult } from "../metrics/fileMetrics.js"
import { aggregateDirectories } from "../metrics/directoryAggregator.js"
import { analyzeChurn } from "../metrics/churnAnalyzer.js"
import { hasAllowedExtension } from "../utils/fsHelpers.js"
import { promisePool } from "../utils/promisePool.js"
import { DEFAULT_CONFIG, type RepoIndexConfig } from "../config/config.js"
import { indexSchema } from "../types/indexSchema.js"

export async function buildIndex(
  userConfig: Partial<RepoIndexConfig>
) {
  if (!userConfig.rootPath) {
    throw new Error("rootPath must be specified")
  }

  const config: RepoIndexConfig = {
    ...DEFAULT_CONFIG,
    ...userConfig,
    rootPath: userConfig.rootPath
  }

  const filePaths: string[] = []

  for await (const relativePath of walkFiles(config.rootPath)) {
    if (!hasAllowedExtension(relativePath, config.includeExtensions)) continue
    filePaths.push(relativePath)
  }

  const files: FileMetricsResult[] = []
  const directoryMap = new Map<
    string,
    {
      fileCount: number
      totalLines: number
      codeLines: number
      commentLines: number
      blankLines: number
    }
  >()

  await promisePool(
    filePaths,
    async (relativePath) => {
      const result = await analyzeFile(
        config.rootPath,
        relativePath,
        { includeBinaryAnalysis: config.includeBinaryAnalysis }
      )

      if (!result) return

      if (config.enableGit) {
        result.churn = await analyzeChurn(
          config.rootPath,
          relativePath
        )
      }

      files.push(result)
      aggregateDirectories(relativePath, result.loc, directoryMap)
    },
    config.parallelism
  )

  const index = {
    repo: {
      path: config.rootPath,
      name: path.basename(config.rootPath),
      generatedAt: new Date().toISOString()
    },
    files,
    directories: Object.fromEntries(directoryMap)
  }

  indexSchema.parse(index)

  return index
}