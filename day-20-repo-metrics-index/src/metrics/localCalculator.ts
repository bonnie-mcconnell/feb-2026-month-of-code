import fs from "node:fs/promises"
import path from "node:path"
import { isBinaryFile } from "../walker/binaryDetector.js"
import type { FileLOCStats } from "../types/metrics.js"

export async function calculateLOC(
  rootPath: string,
  relativePath: string,
  includeBinaryAnalysis: boolean
): Promise<FileLOCStats | null> {

  if (!includeBinaryAnalysis) {
    if (await isBinaryFile(rootPath, relativePath)) {
      return null
    }
  }

  const fullPath = path.join(rootPath, relativePath)
  const content = await fs.readFile(fullPath, "utf8")

  const linesArray = content.replace(/\r?\n$/, "").split(/\r?\n/)

  let total = 0
  let code = 0
  let comments = 0
  let blank = 0
  let inBlockComment = false

  for (const line of linesArray) {
    total++
    const trimmed = line.trim()

    if (!trimmed) {
      blank++
      continue
    }

    if (inBlockComment) {
      comments++
      if (trimmed.includes("*/")) {
        inBlockComment = false
      }
      continue
    }

    if (trimmed.startsWith("//") || trimmed.startsWith("#")) {
      comments++
      continue
    }

    if (trimmed.startsWith("/*")) {
      comments++
      if (!trimmed.includes("*/")) {
        inBlockComment = true
      }
      continue
    }

    code++
  }

  return { total, code, comments, blank }
}