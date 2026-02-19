import type {
  CommitMetrics,
  ContributorMetrics,
  IssueMetrics,
  PRMetrics,
  StalenessMetrics
} from "../types/metrics.js"

export function generateRiskFlags(
  commit: CommitMetrics,
  contributors: ContributorMetrics,
  issues: IssueMetrics,
  prs: PRMetrics,
  staleness: StalenessMetrics
): string[] {
  const flags: string[] = []

  if (staleness.daysSinceLastCommit > 180) {
    flags.push("No commits in 6+ months")
  }

  if (staleness.daysSinceLastRelease !== null &&
      staleness.daysSinceLastRelease > 365) {
    flags.push("No release in over a year")
  }

  if (contributors.topContributorShare > 0.8) {
    flags.push("Single contributor dominance risk")
  }

  if (issues.staleIssueRatio > 0.5) {
    flags.push("High stale issue ratio")
  }

  if (prs.stalePRRatio > 0.4) {
    flags.push("High stale PR ratio")
  }

  if (commit.activityTrendRatio < 0.5) {
    flags.push("Commit activity declining significantly")
  }

  return flags
}
