import { execFile } from "node:child_process"
import { promisify } from "node:util"

const execFileAsync = promisify(execFile)

export async function getGitChurn(
  repoPath: string,
  filePath: string
): Promise<number> {
  try {
    const { stdout } = await execFileAsync("git", [
      "-C",
      repoPath,
      "log",
      "--follow",
      "--pretty=format:",
      "--name-only",
      filePath
    ])

    const lines = stdout.trim().split("\n").filter(Boolean)
    return lines.length
  } catch {
    return 0
  }
}