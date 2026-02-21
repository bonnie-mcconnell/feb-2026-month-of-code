import {
  UnifiedMetricsV1,
  UNIFIED_METRICS_VERSION,
} from "../schema/unifiedMetrics"

import {
  defaultConfig,
  DashboardConfig,
  validateWeights,
} from "../config/config"

import {
  NormalizedUptimeMetrics,
  NormalizedJobMetrics,
  NormalizedRepositoryMetrics,
  NormalizedRepoHealthMetrics,
} from "../schema/internalTypes"

import {
  evaluateUptimeRisk,
  evaluateJobRisk,
  evaluateRepositoryRisk,
  evaluateRepoHealthRisk,
  computeCrossSignalBoost,
  computeOverallRisk,
} from "./riskEvaluator"

export interface AggregationInput {
  uptime?: NormalizedUptimeMetrics
  jobs?: NormalizedJobMetrics
  repository?: NormalizedRepositoryMetrics
  repoHealth?: NormalizedRepoHealthMetrics
  config?: DashboardConfig
  now?: () => string
}

export function aggregateMetrics(
  input: AggregationInput
): UnifiedMetricsV1 {

  const timestamp = input.now
    ? input.now()
    : new Date().toISOString()

  const config = input.config ?? defaultConfig

  // validate before use
  validateWeights(config.subsystemWeights)

  let uptimeSection: UnifiedMetricsV1["uptime"]
  let jobsSection: UnifiedMetricsV1["jobs"]
  let repositorySection: UnifiedMetricsV1["repository"]
  let repoHealthSection: UnifiedMetricsV1["repoHealth"]

  let uptimeRisk: number | undefined
  let jobRisk: number | undefined
  let repoRisk: number | undefined
  let healthRisk: number | undefined

  // Uptime
  if (input.uptime) {
    const { uptimeScore, uptimeRisk: risk } =
      evaluateUptimeRisk(input.uptime)

    uptimeRisk = risk

    uptimeSection = {
      ...input.uptime,
      uptimeScore,
    }
  }

  // Jobs
  if (input.jobs) {
    const { jobRisk: risk, jobReliabilityScore } =
      evaluateJobRisk(input.jobs)

    jobRisk = risk

    jobsSection = {
      ...input.jobs,
      jobReliabilityScore,
    }
  }

  // Repository
  if (input.repository) {
    const { repoRisk: risk, maintainabilityScore } =
      evaluateRepositoryRisk(input.repository)

    repoRisk = risk

    repositorySection = {
      ...input.repository,
      maintainabilityScore,
    }
  }

  // Repo Health
  if (input.repoHealth) {
    const { healthRisk: risk, activityScore } =
      evaluateRepoHealthRisk(input.repoHealth)

    healthRisk = risk

    repoHealthSection = {
      ...input.repoHealth,
      activityScore,
    }
  }

  const crossSignalBoost = computeCrossSignalBoost({
    uptime: input.uptime,
    jobs: input.jobs,
    repository: input.repository,
    repoHealth: input.repoHealth,
  })

  const { overallRiskScore, overallHealthScore } =
    computeOverallRisk({
      uptimeRisk,
      jobRisk,
      repoRisk,
      healthRisk,
      crossSignalBoost,
      config
    })

  return {
    system: {
      version: UNIFIED_METRICS_VERSION,
      generatedAt: timestamp,
      sources: {
        uptime: Boolean(input.uptime),
        jobs: Boolean(input.jobs),
        repository: Boolean(input.repository),
        repoHealth: Boolean(input.repoHealth),
      },
    },
    uptime: uptimeSection,
    jobs: jobsSection,
    repository: repositorySection,
    repoHealth: repoHealthSection,
    overallRiskScore,
    overallHealthScore,
  }
}