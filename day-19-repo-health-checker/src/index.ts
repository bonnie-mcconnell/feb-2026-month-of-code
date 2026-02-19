import { GitHubClient, fetchLatestRelease } from "./github/githubClient.js"
import { paginate } from "./github/pagination.js"
import { mapIssue, mapPR } from "./github/mappers.js"

import { analyzeCommits } from "./analyzers/commitAnalyzer.js"
import { analyzeContributors } from "./analyzers/contributorAnalyzer.js"
import { analyzeIssues } from "./analyzers/issueAnalyzer.js"
import { analyzePRs } from "./analyzers/prAnalyzer.js"
import { analyzeStaleness } from "./analyzers/stalenessAnalyzer.js"

import {
  scoreCommitActivity,
  scoreContributorDistribution,
  scoreIssueHealth,
  scorePRHealth,
  scoreStalenessRisk,
  calculateOverallScore
} from "./scoring/scoringEngine.js"

import { generateRiskFlags } from "./scoring/riskFlags.js"

import type { ScoringWeights } from "./scoring/scoringModel.js"
import type {
  CommitMetrics,
  ContributorMetrics,
  IssueMetrics,
  PRMetrics,
  StalenessMetrics
} from "./types/metrics.js"

import type { RiskFlag } from "./types/risk.js"

export interface RepoAnalysisOptions {
  owner: string
  repo: string
  token?: string
  now?: Date
  weights?: Partial<ScoringWeights>
  windowDays?: number
}

export interface RepoHealthReport {
  commitMetrics: CommitMetrics
  contributorMetrics: ContributorMetrics
  issueMetrics: IssueMetrics
  prMetrics: PRMetrics
  stalenessMetrics: StalenessMetrics
  riskFlags: RiskFlag[]
  scores: {
    commitActivity: number
    contributorDistribution: number
    issueHealth: number
    prHealth: number
    stalenessRisk: number
  }
  overallScore: number
}

const DEFAULT_WEIGHTS: ScoringWeights = {
  commitActivity: 0.2,
  contributorDistribution: 0.2,
  issueHealth: 0.2,
  prHealth: 0.2,
  stalenessRisk: 0.2
}

function normalizeWeights(
  weights?: Partial<ScoringWeights>
): ScoringWeights {
  const merged = { ...DEFAULT_WEIGHTS, ...weights }

  const total =
    merged.commitActivity +
    merged.contributorDistribution +
    merged.issueHealth +
    merged.prHealth +
    merged.stalenessRisk

  return {
    commitActivity: merged.commitActivity / total,
    contributorDistribution: merged.contributorDistribution / total,
    issueHealth: merged.issueHealth / total,
    prHealth: merged.prHealth / total,
    stalenessRisk: merged.stalenessRisk / total
  }
}

export async function analyzeRepository(
  opts: RepoAnalysisOptions
): Promise<RepoHealthReport> {
  const {
    owner,
    repo,
    now = new Date(),
    windowDays = 90
  } = opts

  const client =
    opts.token !== undefined
      ? new GitHubClient({ token: opts.token })
      : new GitHubClient()

  // ---- PARALLEL FETCHING ----
  const [
    apiCommits,
    apiContributors,
    apiIssues,
    apiPRs,
    lastReleaseDate
  ] = await Promise.all([
    paginate(page =>
      client.request<any[]>(
        `/repos/${owner}/${repo}/commits?per_page=100&page=${page}`
      )
    ),
    paginate(page =>
      client.request<any[]>(
        `/repos/${owner}/${repo}/contributors?per_page=100&page=${page}`
      )
    ),
    paginate(page =>
      client.request<any[]>(
        `/repos/${owner}/${repo}/issues?state=all&per_page=100&page=${page}`
      )
    ),
    paginate(page =>
      client.request<any[]>(
        `/repos/${owner}/${repo}/pulls?state=all&per_page=100&page=${page}`
      )
    ),
    fetchLatestRelease(client, owner, repo)
  ])

  // ---- ANALYSIS ----
  const commitMetrics = analyzeCommits(apiCommits, {
    now,
    windowDays
  })

  const contributorMetrics = analyzeContributors(apiContributors)

  const issueMetrics = analyzeIssues(
    apiIssues.map(mapIssue),
    now
  )

  const prMetrics = analyzePRs(
    apiPRs.map(mapPR),
    now
  )

  const lastCommitDate =
    commitMetrics.lastCommitDate !== null
      ? new Date(commitMetrics.lastCommitDate)
      : null

  const stalenessMetrics = analyzeStaleness(
    lastCommitDate,
    lastReleaseDate,
    issueMetrics.openIssuesCount > 0,
    prMetrics.openPRCount > 0,
    now
  )

  // ---- SCORING ----
  const weights = normalizeWeights(opts.weights)

  const scores = {
    commitActivity: scoreCommitActivity(commitMetrics),
    contributorDistribution:
      scoreContributorDistribution(contributorMetrics),
    issueHealth: scoreIssueHealth(issueMetrics),
    prHealth: scorePRHealth(prMetrics),
    stalenessRisk: scoreStalenessRisk(stalenessMetrics)
  }

  const overallScore = calculateOverallScore(scores, weights)

  const riskFlags = generateRiskFlags(
    commitMetrics,
    contributorMetrics,
    issueMetrics,
    prMetrics,
    stalenessMetrics
  )

  return {
    commitMetrics,
    contributorMetrics,
    issueMetrics,
    prMetrics,
    stalenessMetrics,
    scores,
    riskFlags,
    overallScore
  }
}
