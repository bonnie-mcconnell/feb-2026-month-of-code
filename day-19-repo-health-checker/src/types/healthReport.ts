import type {
  CommitMetrics,
  ContributorMetrics,
  IssueMetrics,
  PRMetrics,
  StalenessMetrics
} from "./metrics.js";

export interface CategoryScores {
  commitActivity: number;
  contributorDistribution: number;
  issueHealth: number;
  prHealth: number;
  stalenessRisk: number;
  overall: number;
}

export interface HealthReport {
  repository: string;
  generatedAt: string;

  metrics: {
    commitActivity: CommitMetrics;
    contributorDistribution: ContributorMetrics;
    issueHealth: IssueMetrics;
    prHealth: PRMetrics;
    stalenessRisk: StalenessMetrics;
  };

  scores: CategoryScores;

  riskFlags: string[];
}
