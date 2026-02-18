export interface ScoringWeights {
  commitActivity: number;
  contributorDistribution: number;
  issueHealth: number;
  prHealth: number;
  stalenessRisk: number;
}

export const DEFAULT_WEIGHTS: ScoringWeights = {
  commitActivity: 0.25,
  contributorDistribution: 0.20,
  issueHealth: 0.20,
  prHealth: 0.20,
  stalenessRisk: 0.15
};
