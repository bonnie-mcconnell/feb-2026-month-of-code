import fs from "node:fs/promises"
import path from "node:path"
import { calculateLOC } from "./localCalculator.js"
import { estimateComplexity } from "./complexityEstimator.js"
import type { FileLOCStats } from "../types/metrics.js"
import { analyzeDependencies } from "./dependencyAnalyzer.js"

export interface FileMetricsResult {
  path: string
  loc: FileLOCStats
  complexity: number
  dependencies: {
    internal: number
    external: number
  }
  churn?: number
}

interface AnalyzeFileOptions {
  includeBinaryAnalysis: boolean
}

export async function analyzeFile(
  rootPath: string,
  relativePath: string,
  options: AnalyzeFileOptions
): Promise<FileMetricsResult | null> {

  const loc = await calculateLOC(
    rootPath,
    relativePath,
    options.includeBinaryAnalysis
  )

  if (!loc) return null

  const fullPath = path.join(rootPath, relativePath)
  const source = await fs.readFile(fullPath, "utf8")

  const complexity = estimateComplexity(source)

  const dependencies = await analyzeDependencies(
    rootPath,
    relativePath
  )

  return {
    path: relativePath,
    loc,
    complexity,
    dependencies
  }
}