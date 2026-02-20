import fs from "node:fs/promises"
import path from "node:path"
import { calculateLOC } from "./localCalculator.js"
import { estimateComplexity } from "./complexityEstimator.js"
import type { FileLOCStats } from "../types/metrics.js"

export interface FileMetricsResult {
  path: string
  loc: FileLOCStats
  complexity: number
}

export async function analyzeFile(
  rootPath: string,
  relativePath: string
): Promise<FileMetricsResult | null> {
  const loc = await calculateLOC(rootPath, relativePath)
  if (!loc) return null

  const fullPath = path.join(rootPath, relativePath)
  const source = await fs.readFile(fullPath, "utf8")

  const complexity = estimateComplexity(source)

  return {
    path: relativePath,
    loc,
    complexity
  }
}