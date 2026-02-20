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

export interface FileLOCStats {
  total: number
  code: number
  comments: number
  blank: number
}

export interface DirectoryMetrics {
  fileCount: number
  totalLines: number
  codeLines: number
  commentLines: number
  blankLines: number
}