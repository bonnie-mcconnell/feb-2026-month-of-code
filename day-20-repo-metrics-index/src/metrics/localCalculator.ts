import fs from "node:fs"
import readline from "node:readline"
import path from "node:path"
import { isBinaryFile } from "../walker/binaryDetector.js"
import type { FileLOCStats } from "../types/metrics.js"

export async function calculateLOC(
  rootPath: string,
  relativePath: string
): Promise<FileLOCStats | null> {
  if (await isBinaryFile(rootPath, relativePath)) {
    return null
  }

  const fullPath = path.join(rootPath, relativePath)

  const stream = fs.createReadStream(fullPath, { encoding: "utf8" })

  const rl = readline.createInterface({
    input: stream,
    crlfDelay: Infinity
  })

  let total = 0
  let code = 0
  let comments = 0
  let blank = 0
  let inBlockComment = false

  for await (const line of rl) {
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