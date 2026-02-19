export interface CommitMetrics {
  commitsLast30Days: number;
  commitsLast90Days: number;
  avgCommitsPerWeek: number;
  activityTrendRatio: number; // 30d vs 90d normalized
  lastCommitDate: Date | null;
}

export interface ContributorMetrics {
  totalContributors: number;
  topContributorShare: number; // 0–1
  concentrationIndex: number; // 0–1 simplified gini
}

export interface IssueMetrics {
  openIssuesCount: number;
  medianOpenIssueAgeDays: number;
  staleIssueRatio: number; // >90 days
  closeToOpenRatio: number; // recent window
}

export interface PRMetrics {
  openPRCount: number;
  avgTimeToMergeDays: number;
  mergeRatio: number; // merged/closed
  stalePRRatio: number; // >30 days
}

export interface StalenessMetrics {
  daysSinceLastCommit: number;
  daysSinceLastRelease: number | null;
  recentIssueActivity: boolean;
  recentPRActivity: boolean;
}
