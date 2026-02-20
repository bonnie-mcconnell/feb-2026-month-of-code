import fs from "node:fs/promises"
import path from "node:path"
import { walkFiles } from "../walker/fileWalker.js"
import { analyzeFile, type FileMetricsResult } from "../metrics/fileMetrics.js"
import { aggregateDirectories } from "../metrics/directoryAggregator.js"
import { analyzeChurn } from "../metrics/churnAnalyzer.js"
import { hasAllowedExtension } from "../utils/fsHelpers.js"
import { promisePool } from "../utils/promisePool.js"
import { DEFAULT_CONFIG, type RepoIndexConfig } from "../config/config.js"
import { indexSchema } from "../types/indexSchema.js"
import { analyzeDependencies, type DependencyStats } from "../metrics/dependencyAnalyzer.js"

export async function buildIndex(userConfig: Partial<RepoIndexConfig>) {
  if (!userConfig.rootPath) {
    throw new Error("rootPath must be specified")
  }

  const config: RepoIndexConfig = {
    ...DEFAULT_CONFIG,
    ...userConfig,
    rootPath: userConfig.rootPath
  }

  // 1️⃣ Collect file paths
  const filePaths: string[] = []
  for await (const relativePath of walkFiles(config.rootPath)) {
    if (!hasAllowedExtension(relativePath, config.includeExtensions)) continue
    filePaths.push(relativePath)
  }

  // 2️⃣ Prepare aggregation containers
  const files: FileMetricsResult[] = []
  const directoryMap = new Map<
    string,
    {
      fileCount: number
      totalLines: number
      codeLines: number
      commentLines: number
      blankLines: number
      internalDeps: number
      externalDeps: number
    }
  >()

  // 3️⃣ Process files in parallel
  await promisePool(
    filePaths,
    async (relativePath) => {
      const fileMetrics = await analyzeFile(config.rootPath, relativePath, {
        includeBinaryAnalysis: config.includeBinaryAnalysis
      })
      if (!fileMetrics) return

      // Add Git churn if enabled
      if (config.enableGit) {
        fileMetrics.churn = await analyzeChurn(config.rootPath, relativePath)
      }

      // Add dependency counts
      const deps: DependencyStats = await analyzeDependencies(config.rootPath, relativePath)

      // Store in fileMetrics
      fileMetrics.dependencies = deps

      files.push(fileMetrics)

      // Aggregate per-directory metrics
      const dirStats = {
        ...fileMetrics.loc,
        internalDeps: deps.internal,
        externalDeps: deps.external
      }
      aggregateDirectories(relativePath, dirStats, directoryMap)
    },
    config.parallelism
  )

  // 4️⃣ Construct final index
  const index = {
    repo: {
      path: config.rootPath,
      name: path.basename(config.rootPath),
      generatedAt: new Date().toISOString()
    },
    files,
    directories: Object.fromEntries(directoryMap)
  }

  indexSchema.parse(index) // Validate schema

  return index
}