import fs from "node:fs/promises"
import path from "node:path"

export async function isBinaryFile(rootPath: string, relativePath: string) {
  const fullPath = path.join(rootPath, relativePath)
  const buffer = await fs.readFile(fullPath)

  const sample = buffer.subarray(0, 512)

  for (const byte of sample) {
    if (byte === 0) return true
  }

  return false
}