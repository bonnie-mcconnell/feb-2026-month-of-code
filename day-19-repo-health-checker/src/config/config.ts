import type { ScoringWeights } from "../scoring/scoringModel.js"

export const DEFAULT_SCORING_WEIGHTS: ScoringWeights = {
  commitActivity: 0.2,
  contributorDistribution: 0.2,
  issueHealth: 0.2,
  prHealth: 0.2,
  stalenessRisk: 0.2
}

export const DEFAULT_ANALYSIS_WINDOW_DAYS = 90
