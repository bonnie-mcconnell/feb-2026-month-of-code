import type {
  CommitMetrics,
  ContributorMetrics,
  IssueMetrics,
  PRMetrics,
  StalenessMetrics
} from "../types/metrics.js";

import type {
  CategoryScores
} from "../types/healthReport.js";

import type {
  ScoringWeights
} from "./scoringModel.js";

/* ----------------------------- Utilities ----------------------------- */

function clamp(value: number, min = 0, max = 100): number {
  return Math.max(min, Math.min(max, value));
}

/* ------------------------ Category Scoring --------------------------- */

/**
 * Commit Activity Scoring Philosophy:
 *
 * - Zero commits in 90 days = score 0 (inactive)
 * - Recent commits in last 30 days = strong positive signal
 * - Sustained weekly activity increases score
 * - Trend ratio rewards sustained vs burst activity
 * - Cap frequency influence to prevent spam inflation
 */
export function scoreCommitActivity(
  metrics: CommitMetrics
): number {
  if (metrics.commitsLast90Days === 0) {
    return 0;
  }

  const recentActivityScore =
    metrics.commitsLast30Days > 0 ? 40 : 10;

  // Cap impact of extremely high commit volume
  const frequencyScore =
    clamp(Math.min(metrics.avgCommitsPerWeek, 10) * 5);

  const trendScore =
    clamp(metrics.activityTrendRatio * 30);

  return clamp(
    recentActivityScore +
    frequencyScore +
    trendScore
  );
}

/**
 * Contributor Distribution Scoring Philosophy:
 *
 * - Single contributor = centralization risk
 * - Lower topContributorShare = better distribution
 * - Lower concentrationIndex = healthier diversity
 */
export function scoreContributorDistribution(
  metrics: ContributorMetrics
): number {
  if (metrics.totalContributors <= 1) {
    return 20; // strong penalty
  }

  const distributionScore =
    (1 - metrics.topContributorShare) * 50;

  const diversityScore =
    (1 - metrics.concentrationIndex) * 50;

  return clamp(distributionScore + diversityScore);
}

/**
 * Issue Health Scoring Philosophy:
 *
 * - closeToOpenRatio >= 1 -> backlog stable or shrinking
 * - staleIssueRatio high -> penalty
 * - median age high -> gradual decay
 */
export function scoreIssueHealth(
  metrics: IssueMetrics
): number {
  const backlogScore =
    clamp(metrics.closeToOpenRatio * 40);

  const freshnessScore =
    (1 - metrics.staleIssueRatio) * 40;

  const ageComponent =
    clamp(30 - metrics.medianOpenIssueAgeDays / 3);

  return clamp(
    backlogScore +
    freshnessScore +
    ageComponent
  );
}

/**
 * PR Health Scoring Philosophy:
 *
 * - High mergeRatio -> healthy review process
 * - Low stalePRRatio -> active collaboration
 * - Faster avgTimeToMerge -> good velocity
 */
export function scorePRHealth(
  metrics: PRMetrics
): number {
  const mergeScore =
    metrics.mergeRatio * 40;

  const freshnessScore =
    (1 - metrics.stalePRRatio) * 30;

  const speedScore =
    clamp(30 - metrics.avgTimeToMergeDays);

  return clamp(
    mergeScore +
    freshnessScore +
    speedScore
  );
}

/**
 * Staleness Scoring Philosophy:
 *
 * - Long time since last commit -> decay
 * - Long time since last release -> decay
 * - Recent issue/PR activity mitigates decay
 */
export function scoreStalenessRisk(
  metrics: StalenessMetrics
): number {
  const commitDecay =
    clamp(50 - metrics.daysSinceLastCommit / 3);

  const releaseDecay =
    metrics.daysSinceLastRelease !== null
      ? clamp(30 - metrics.daysSinceLastRelease / 5)
      : 10;

  const collaborationSignal =
    metrics.recentIssueActivity ||
    metrics.recentPRActivity
      ? 20
      : 0;

  return clamp(
    commitDecay +
    releaseDecay +
    collaborationSignal
  );
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
      weights.stalenessRisk;

  return clamp(total);
}