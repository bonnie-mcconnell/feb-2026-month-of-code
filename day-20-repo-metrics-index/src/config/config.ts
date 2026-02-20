export interface RepoIndexConfig {
  rootPath: string
  churnWindowDays: number
  minChurnThreshold?: number
  includeBinaryAnalysis: boolean
  includeExtensions: string[] | null
  parallelism: number
  enableGit: boolean
}

export const DEFAULT_CONFIG: Omit<RepoIndexConfig, "rootPath"> = {
  churnWindowDays: 90,
  includeBinaryAnalysis: true,
  includeExtensions: null, // null = include all
  parallelism: 4,
  enableGit: true
}