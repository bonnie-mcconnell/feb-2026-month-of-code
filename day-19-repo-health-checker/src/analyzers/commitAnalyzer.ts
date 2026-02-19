import type { CommitMetrics } from "../types/metrics.js";

export interface NormalizedCommit {
  authoredDate: Date;
}

export interface CommitAnalyzerOptions {
  windowDays: number; // typically 90
  now?: Date;         // injected for deterministic tests
}

/**
 * Commit Analyzer
 *
 * Computes:
 * - commits in last 30 days
 * - commits in last N days (window)
 * - average commits per week
 * - activity trend ratio (30d vs N/3 baseline)
 * - last commit date
 *
 * No scoring logic here.
 */
export function analyzeCommits(
  commits: NormalizedCommit[],
  options: CommitAnalyzerOptions
): CommitMetrics {
  const now = options.now ?? new Date();
  const windowDays = options.windowDays;

  const windowStart = new Date(
    now.getTime() - windowDays * 24 * 60 * 60 * 1000
  );

  const thirtyDayStart = new Date(
    now.getTime() - 30 * 24 * 60 * 60 * 1000
  );

  const commitsInWindow = commits.filter(
    (c) => c.authoredDate >= windowStart
  );

  const commitsLast30Days = commits.filter(
    (c) => c.authoredDate >= thirtyDayStart
  ).length;

  const commitsLast90Days = commitsInWindow.length;

  const avgCommitsPerWeek =
    windowDays > 0
      ? commitsLast90Days / (windowDays / 7)
      : 0;

  // Expected 30-day baseline if evenly distributed
  const expected30Day =
    commitsLast90Days / (windowDays / 30 || 1);

  const activityTrendRatio =
    expected30Day > 0
      ? commitsLast30Days / expected30Day
      : 0;

  const lastCommitDate =
    commits.length > 0
      ? new Date(
          Math.max(
            ...commits.map((c) => c.authoredDate.getTime())
          )
        )
      : null;

  return {
    commitsLast30Days,
    commitsLast90Days,
    avgCommitsPerWeek,
    activityTrendRatio,
    lastCommitDate
  };
}
