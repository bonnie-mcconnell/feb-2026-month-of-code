export interface RepoIndexConfig {
  rootPath: string

  // Git / churn
  churnWindowDays: number
  minChurnThreshold?: number
  enableGit: boolean

  // File processing
  includeBinaryAnalysis: boolean
  includeExtensions: string[] | null
  parallelism: number
}

export const DEFAULT_CONFIG: Omit<RepoIndexConfig, "rootPath"> = {
  churnWindowDays: 90,
  minChurnThreshold: undefined,
  enableGit: true,

  includeBinaryAnalysis: true,
  includeExtensions: null,
  parallelism: 4
}