import path from "node:path"
import type { FileLOCStats, DirectoryMetrics } from "../types/metrics.js"

export function aggregateDirectories(
  filePath: string,
  lines: FileLOCStats,
  directoryMap: Map<string, DirectoryMetrics>
) {
  const normalized = filePath.split(path.sep).join("/")
  const segments = normalized.split("/")
  segments.pop()

  let currentPath = ""

  for (const segment of segments) {
    currentPath = currentPath
      ? `${currentPath}/${segment}`
      : segment

    const existing = directoryMap.get(currentPath) ?? {
      fileCount: 0,
      totalLines: 0,
      codeLines: 0,
      commentLines: 0,
      blankLines: 0
    }

    existing.fileCount += 1
    existing.totalLines += lines.total
    existing.codeLines += lines.code
    existing.commentLines += lines.comments
    existing.blankLines += lines.blank

    directoryMap.set(currentPath, existing)
  }
}