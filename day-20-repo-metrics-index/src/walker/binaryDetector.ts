import fs from "node:fs/promises"
import path from "node:path"

const SAMPLE_SIZE = 512

export async function isBinaryFile(
  rootPath: string,
  relativePath: string
): Promise<boolean> {
  const fullPath = path.join(rootPath, relativePath)

  let fd
  try {
    fd = await fs.open(fullPath, "r")

    const buffer = Buffer.alloc(SAMPLE_SIZE)
    const { bytesRead } = await fd.read(buffer, 0, SAMPLE_SIZE, 0)

    for (let i = 0; i < bytesRead; i++) {
      if (buffer[i] === 0) {
        return true
      }
    }

    return false
  } finally {
    await fd?.close()
  }
}