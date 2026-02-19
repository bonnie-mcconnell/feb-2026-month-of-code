export interface RepoMetadata {
  path: string
  name: string
  generatedAt: string // ISO 8601 UTC
}

export interface SummaryMetrics {
  totalFiles: number
  textFiles: number
  binaryFiles: number

  totalLines: number
  codeLines: number
  commentLines: number
  blankLines: number
}

export interface ExtensionCounts {
  [extension: string]: number
}

export interface DirectoryFileCounts {
  [topLevelDir: string]: number
}

export interface DirectoryMetrics {
  fileCount: number
  totalLines: number
  codeLines: number
  commentLines: number
  blankLines: number
  churn?: {
    additions: number
    deletions: number
  }
}

export interface DirectoryIndex {
  [directoryPath: string]: DirectoryMetrics
}

export interface FileChurnMetrics {
  additions: number
  deletions: number
}

export interface ChurnIndex {
  windowDays: number
  files: Record<string, FileChurnMetrics>
  topChurnFiles: Array<{
    path: string
    churn: number
  }>
}

export interface DependencySummary {
  external: {
    count: number
    names: string[]
  }
  internal: {
    moduleCount: number
    avgImportsPerFile: number
    maxImportsPerFile: number
  }
}

export interface FileComplexityMetrics {
  functionCount: number
  avgFunctionLength: number
  maxFunctionLength: number
  maxNestingDepth: number
  cyclomaticEstimate: number
}

export interface ComplexityIndex {
  files: Record<string, FileComplexityMetrics>
  aggregate: {
    avgCyclomatic: number
    maxCyclomatic: number
  }
}

export interface RepoIndex {
  schemaVersion: "1.0.0"

  repo: RepoMetadata

  summary: SummaryMetrics

  files: {
    byExtension: ExtensionCounts
    byTopLevelDirectory: DirectoryFileCounts
  }

  directories: DirectoryIndex

  churn: ChurnIndex | null

  dependencies: DependencySummary

  complexity: ComplexityIndex
}