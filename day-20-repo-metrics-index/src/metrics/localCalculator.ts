import fs from "node:fs"
import readline from "node:readline"
import path from "node:path"

export interface LineMetrics {
  total: number
  code: number
  comment: number
  blank: number
}

export async function calculateLOC(
  rootPath: string,
  relativePath: string
): Promise<LineMetrics> {
  const fullPath = path.join(rootPath, relativePath)

  const stream = fs.createReadStream(fullPath, { encoding: "utf8" })

  const rl = readline.createInterface({
    input: stream,
    crlfDelay: Infinity
  })

  let total = 0
  let code = 0
  let comment = 0
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
      comment++
      if (trimmed.includes("*/")) {
        inBlockComment = false
      }
      continue
    }

    if (
      trimmed.startsWith("//") ||
      trimmed.startsWith("#")
    ) {
      comment++
      continue
    }

    if (trimmed.startsWith("/*")) {
      comment++
      if (!trimmed.includes("*/")) {
        inBlockComment = true
      }
      continue
    }

    code++
  }

  return { total, code, comment, blank }
}