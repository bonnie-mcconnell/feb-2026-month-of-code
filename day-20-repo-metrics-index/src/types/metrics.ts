export interface FileLineMetrics {
  total: number
  code: number
  comment: number
  blank: number
}

export interface FileMetrics {
  path: string
  extension: string
  isBinary: boolean
  lines?: FileLineMetrics
}

export interface RawGitNumstatEntry {
  additions: number
  deletions: number
  path: string
}