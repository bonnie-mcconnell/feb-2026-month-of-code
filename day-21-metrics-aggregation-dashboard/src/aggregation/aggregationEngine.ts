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

import { classifyRiskTier } from "../utils/riskTier"

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

  const timestamp =
    input.now?.() ?? new Date().toISOString()

  const config = input.config ?? defaultConfig
  validateWeights(config.subsystemWeights)

  let uptimeRisk: number | undefined
  let jobRisk: number | undefined
  let repoRisk: number | undefined
  let healthRisk: number | undefined

  const uptimeSection = input.uptime
    ? (() => {
        const { uptimeScore, uptimeRisk: risk } =
          evaluateUptimeRisk(input.uptime!)
        uptimeRisk = risk
        return { ...input.uptime!, uptimeScore }
      })()
    : undefined

  const jobsSection = input.jobs
    ? (() => {
        const { jobRisk: risk, jobReliabilityScore } =
          evaluateJobRisk(input.jobs!)
        jobRisk = risk
        return { ...input.jobs!, jobReliabilityScore }
      })()
    : undefined

  const repositorySection = input.repository
    ? (() => {
        const { repoRisk: risk, maintainabilityScore } =
          evaluateRepositoryRisk(input.repository!)
        repoRisk = risk
        return { ...input.repository!, maintainabilityScore }
      })()
    : undefined

  const repoHealthSection = input.repoHealth
    ? (() => {
        const { healthRisk: risk, activityScore } =
          evaluateRepoHealthRisk(input.repoHealth!)
        healthRisk = risk
        return { ...input.repoHealth!, activityScore }
      })()
    : undefined

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
      config,
    })

  const riskTier = classifyRiskTier(overallRiskScore)

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
      riskTier,
    },

    uptime: uptimeSection,
    jobs: jobsSection,
    repository: repositorySection,
    repoHealth: repoHealthSection,

    overallRiskScore,
    overallHealthScore,
  }
}