export interface RepoIndexConfig {
  rootPath: string
  churnWindowDays: number
  minChurnThreshold?: number
  includeBinaryAnalysis: boolean
}

export const DEFAULT_CONFIG: Omit<RepoIndexConfig, "rootPath"> = {
  churnWindowDays: 90,
  includeBinaryAnalysis: true
}