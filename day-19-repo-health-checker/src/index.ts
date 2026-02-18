import { GitHubClient } from "./github/githubClient.js"
import { paginate } from "./github/pagination.js"
import { mapIssue, mapPR } from "./github/mappers.js"

import { analyzeIssues } from "./analyzers/issueAnalyzer.js"
import { analyzePRs } from "./analyzers/prAnalyzer.js"
import { analyzeStaleness } from "./analyzers/stalenessAnalyzer.js"

import type { CommitMetrics, IssueMetrics, PRMetrics, StalenessMetrics } from "./types/metrics.js"
import { calculateOverallScore } from "./scoring/scoringEngine.js"
import type { ScoringWeights } from "./scoring/scoringModel.js"

// Example weights - later move to config.ts
const defaultWeights: ScoringWeights = {
  commitActivity: 0.2,
  contributorDistribution: 0.2,
  issueHealth: 0.2,
  prHealth: 0.2,
  stalenessRisk: 0.2
}

export interface RepoAnalysisOptions {
  owner: string
  repo: string
  token?: string
  now?: Date
}

// ---- main function ----
export async function analyzeRepository(opts: RepoAnalysisOptions) {
  const { owner, repo, token, now = new Date() } = opts
  const client = new GitHubClient({ token })

  // ---- Fetch issues ----
  const apiIssues = await paginate(page =>
    client.request<any[]>(`/repos/${owner}/${repo}/issues?state=all&per_page=100&page=${page}`)
  )
  const rawIssues = apiIssues.map(mapIssue)
  const issueMetrics: IssueMetrics = analyzeIssues(rawIssues, now)

  // ---- Fetch PRs ----
  const apiPRs = await paginate(page =>
    client.request<any[]>(`/repos/${owner}/${repo}/pulls?state=all&per_page=100&page=${page}`)
  )
  const rawPRs = apiPRs.map(mapPR)
  const prMetrics: PRMetrics = analyzePRs(rawPRs, now)

  // ---- Staleness ----
  const lastCommitDate = null // TODO: integrate commitAnalyzer
  const lastReleaseDate = null // TODO: integrate release fetch
  const stalenessMetrics: StalenessMetrics = analyzeStaleness(
    lastCommitDate,
    lastReleaseDate,
    issueMetrics.openIssuesCount > 0,
    prMetrics.openPRCount > 0,
    now
  )

  return {
    issueMetrics,
    prMetrics,
    stalenessMetrics
  }
}
