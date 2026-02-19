import type {
  CommitMetrics,
  ContributorMetrics,
  IssueMetrics,
  PRMetrics,
  StalenessMetrics
} from "../types/metrics.js"

import type {
  CategoryScores
} from "../types/healthReport.js"

import type {
  ScoringWeights
} from "./scoringModel.js"

import { logisticScore } from "./normalization.js"

/* ----------------------------- Utilities ----------------------------- */

function clamp(value: number, min = 0, max = 100): number {
  return Math.max(min, Math.min(max, value))
}

/* ------------------------ Category Scoring --------------------------- */

/**
 * Commit Activity:
 * Logistic scaling for volume.
 * Penalizes zero 90-day activity.
 */
export function scoreCommitActivity(
  metrics: CommitMetrics
): number {
  if (metrics.commitsLast90Days === 0) {
    return 0
  }

  const volumeScore = logisticScore(
    metrics.commitsLast30Days,
    20,
    0.18
  )

  const frequencyScore = logisticScore(
    metrics.avgCommitsPerWeek,
    5,
    0.6
  )

  const trendScore = clamp(metrics.activityTrendRatio * 100)

  return clamp(
    volumeScore * 0.5 +
    frequencyScore * 0.3 +
    trendScore * 0.2
  )
}

/**
 * Contributor Distribution:
 * Penalizes concentration using inverted ratios.
 */
export function scoreContributorDistribution(
  metrics: ContributorMetrics
): number {
  if (metrics.totalContributors <= 1) {
    return 15
  }

  const distributionScore =
    (1 - metrics.topContributorShare) * 60

  const diversityScore =
    (1 - metrics.concentrationIndex) * 40

  return clamp(distributionScore + diversityScore)
}

/**
 * Issue Health:
 * Logistic for backlog volume,
 * ratio-based freshness,
 * age decay logistic.
 */
export function scoreIssueHealth(
  metrics: IssueMetrics
): number {
  const backlogScore = clamp(
    metrics.closeToOpenRatio * 100
  )

  const freshnessScore =
    (1 - metrics.staleIssueRatio) * 100

  const ageScore = logisticScore(
    -metrics.medianOpenIssueAgeDays,
    -30,
    0.08
  )

  return clamp(
    backlogScore * 0.4 +
    freshnessScore * 0.4 +
    ageScore * 0.2
  )
}

/**
 * PR Health:
 * Merge ratio + stale ratio +
 * logistic merge speed.
 */
export function scorePRHealth(
  metrics: PRMetrics
): number {
  const mergeScore =
    metrics.mergeRatio * 100

  const freshnessScore =
    (1 - metrics.stalePRRatio) * 100

  const speedScore = logisticScore(
    -metrics.avgTimeToMergeDays,
    -7,
    0.25
  )

  return clamp(
    mergeScore * 0.4 +
    freshnessScore * 0.3 +
    speedScore * 0.3
  )
}

/**
 * Staleness:
 * Pure logistic decay on inactivity.
 */
export function scoreStalenessRisk(
  metrics: StalenessMetrics
): number {
  const commitScore = logisticScore(
    -metrics.daysSinceLastCommit,
    -30,
    0.08
  )

  const releaseScore =
    metrics.daysSinceLastRelease !== null
      ? logisticScore(
          -metrics.daysSinceLastRelease,
          -90,
          0.05
        )
      : 40

  const collaborationBonus =
    metrics.recentIssueActivity ||
    metrics.recentPRActivity
      ? 15
      : 0

  return clamp(
    commitScore * 0.6 +
    releaseScore * 0.3 +
    collaborationBonus
  )
}

/* ------------------------ Aggregation Engine ------------------------- */

export function calculateOverallScore(
  categoryScores: Omit<CategoryScores, "overall">,
  weights: ScoringWeights
): number {
  const total =
    categoryScores.commitActivity *
      weights.commitActivity +
    categoryScores.contributorDistribution *
      weights.contributorDistribution +
    categoryScores.issueHealth *
      weights.issueHealth +
    categoryScores.prHealth *
      weights.prHealth +
    categoryScores.stalenessRisk *
      weights.stalenessRisk

  return clamp(total)
}
