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

export function validateWeights(weights: SubsystemWeights) {
  const total =
    weights.uptime +
    weights.jobs +
    weights.repository +
    weights.repoHealth

  if (Math.abs(total - 1) > 0.0001) {
    throw new Error(
      `Subsystem weights must sum to 1. Received: ${total}`
    )
  }
}