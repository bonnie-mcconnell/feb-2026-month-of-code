export interface SubsystemWeights {
  uptime: number
  jobs: number
  repository: number
  repoHealth: number
}

export interface DashboardConfig {
  subsystemWeights: SubsystemWeights
}

export const defaultConfig: DashboardConfig = {
  subsystemWeights: {
    uptime: 0.30,
    jobs: 0.25,
    repository: 0.20,
    repoHealth: 0.25,
  },
}