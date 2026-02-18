import type { ContributorMetrics } from "../types/metrics.js";

export interface NormalizedContributorCommit {
  authorId: string;
}

/**
 * Contributor Analyzer
 *
 * Computes:
 * - total contributors
 * - top contributor share (0–1)
 * - concentration index (simplified Gini-style)
 *
 * Deterministic. No scoring logic here.
 */
export function analyzeContributors(
  commits: NormalizedContributorCommit[]
): ContributorMetrics {
  if (commits.length === 0) {
    return {
      totalContributors: 0,
      topContributorShare: 0,
      concentrationIndex: 0
    };
  }

  const contributionMap = new Map<string, number>();

  for (const commit of commits) {
    contributionMap.set(
      commit.authorId,
      (contributionMap.get(commit.authorId) ?? 0) + 1
    );
  }

  const totalContributors = contributionMap.size;

  const commitCounts = Array.from(contributionMap.values());
  const totalCommits = commitCounts.reduce(
    (sum, count) => sum + count,
    0
  );

  const maxCommits = Math.max(...commitCounts);

  const topContributorShare =
    totalCommits > 0
      ? maxCommits / totalCommits
      : 0;

  // Simplified concentration index (normalized Herfindahl-Hirschman Index style)
  const concentrationIndex =
    totalCommits > 0
      ? commitCounts
          .map((count) => {
            const share = count / totalCommits;
            return share * share;
          })
          .reduce((sum, value) => sum + value, 0)
      : 0;

  return {
    totalContributors,
    topContributorShare,
    concentrationIndex
  };
}
