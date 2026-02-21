import { clampScore, weightedAverage, invertScore } from "../utils/scoreUtils.js"
import {
  NormalizedUptimeMetrics,
  NormalizedJobMetrics,
  NormalizedRepositoryMetrics,
  NormalizedRepoHealthMetrics,
} from "../schema/internalTypes.js"
import { DashboardConfig } from "../config/config.js"


// -----------------------------
// Subsystem Risk Calculations
// -----------------------------

export function evaluateUptimeRisk(
  uptime: NormalizedUptimeMetrics
) {
  const uptimeScore = clampScore(uptime.averageAvailabilityPct)
  const uptimeRisk = invertScore(uptimeScore)

  return {
    uptimeScore,
    uptimeRisk,
  }
}

export function evaluateJobRisk(
  jobs: NormalizedJobMetrics
) {
  const jobRisk = clampScore(
    jobs.failureRatePct * 0.6 +
    jobs.retryRatePct * 0.3 +
    jobs.deadLetterRatePct * 0.1
  )

  const jobReliabilityScore = invertScore(jobRisk)

  return {
    jobRisk,
    jobReliabilityScore,
  }
}

export function evaluateRepositoryRisk(
  repo: NormalizedRepositoryMetrics
) {
  const repoRisk = clampScore(
    repo.complexityScore * 0.6 +
    repo.churnScore * 0.4
  )

  const maintainabilityScore = invertScore(repoRisk)

  return {
    repoRisk,
    maintainabilityScore,
  }
}

export function evaluateRepoHealthRisk(
  health: NormalizedRepoHealthMetrics
) {
  const healthRisk = clampScore(
    (100 - health.healthScore) * 0.7 +
    health.contributorRiskPct * 0.3
  )

  const activityScore = invertScore(health.contributorRiskPct)

  return {
    healthRisk,
    activityScore,
  }
}

// -----------------------------
// Cross-Signal Amplification
// -----------------------------

export function computeCrossSignalBoost(params: {
  uptime?: NormalizedUptimeMetrics
  jobs?: NormalizedJobMetrics
  repository?: NormalizedRepositoryMetrics
  repoHealth?: NormalizedRepoHealthMetrics
}): number {
  let boost = 0

  const { uptime, jobs, repository, repoHealth } = params

  if (
    repository &&
    repository.churnScore > 70 &&
    repository.complexityScore > 70
  ) {
    boost += 10
  }

  if (
    jobs &&
    jobs.failureRatePct > 10 &&
    jobs.retryRatePct > 20
  ) {
    boost += 10
  }

  if (
    uptime &&
    repoHealth &&
    uptime.averageAvailabilityPct < 99 &&
    repoHealth.healthScore < 60
  ) {
    boost += 15
  }

  return boost
}

// -----------------------------
// Overall Risk Aggregation
// -----------------------------
export function computeOverallRisk(params: {
  uptimeRisk?: number
  jobRisk?: number
  repoRisk?: number
  healthRisk?: number
  crossSignalBoost?: number
  config: DashboardConfig
}) {
  const weights = params.config.subsystemWeights

  const weightedInputs: Array<{ value: number; weight: number }> = []

  if (params.uptimeRisk !== undefined) {
    weightedInputs.push({ value: params.uptimeRisk, weight: weights.uptime })
  }

  if (params.jobRisk !== undefined) {
    weightedInputs.push({ value: params.jobRisk, weight: weights.jobs })
  }

  if (params.repoRisk !== undefined) {
    weightedInputs.push({ value: params.repoRisk, weight: weights.repository })
  }

  if (params.healthRisk !== undefined) {
    weightedInputs.push({ value: params.healthRisk, weight: weights.repoHealth })
  }

  const baseRisk = weightedAverage(weightedInputs)

  const boostedRisk = clampScore(
    baseRisk + (params.crossSignalBoost ?? 0)
  )

  const overallHealthScore = invertScore(boostedRisk)

  return {
    overallRiskScore: boostedRisk,
    overallHealthScore,
  }
}