import type { LineMetrics } from "./localCalculator.js"

export interface DirectoryMetrics {
  fileCount: number
  totalLines: number
  codeLines: number
  commentLines: number
  blankLines: number
}

export function aggregateDirectories(
  filePath: string,
  lines: LineMetrics,
  directoryMap: Map<string, DirectoryMetrics>
) {
  const segments = filePath.split("/")

  // Remove file name
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
    existing.commentLines += lines.comment
    existing.blankLines += lines.blank

    directoryMap.set(currentPath, existing)
  }
}