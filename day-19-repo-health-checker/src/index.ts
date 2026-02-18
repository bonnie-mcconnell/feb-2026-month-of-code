import { GitHubClient } from "./github/githubClient.js"
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

import type { ScoringWeights } from "./scoring/scoringModel.js"
import type {
  CommitMetrics,
  ContributorMetrics,
  IssueMetrics,
  PRMetrics,
  StalenessMetrics
} from "./types/metrics.js"

// ---- default scoring weights ----
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

export interface RepoHealthReport {
  commitMetrics: CommitMetrics
  contributorMetrics: ContributorMetrics
  issueMetrics: IssueMetrics
  prMetrics: PRMetrics
  stalenessMetrics: StalenessMetrics
  overallScore: number
}

export async function analyzeRepository(opts: RepoAnalysisOptions): Promise<RepoHealthReport> {
  const { owner, repo, token, now = new Date() } = opts

  const client = token ? new GitHubClient({ token }) : new GitHubClient()

  // ---- Fetch commits ----
  const apiCommits = await paginate(page =>
    client.request<any[]>(`/repos/${owner}/${repo}/commits?per_page=100&page=${page}`)
  )
  const commitMetrics: CommitMetrics = analyzeCommits(apiCommits, { now, windowDays: 90 })

  // ---- Fetch contributors ----
  const apiContributors = await paginate(page =>
    client.request<any[]>(`/repos/${owner}/${repo}/contributors?per_page=100&page=${page}`)
  )
  const contributorMetrics: ContributorMetrics = analyzeContributors(apiContributors)

  // ---- Fetch issues ----
  const apiIssues = await paginate(page =>
    client.request<any[]>(`/repos/${owner}/${repo}/issues?state=all&per_page=100&page=${page}`)
  )
  const issueMetrics: IssueMetrics = analyzeIssues(apiIssues.map(mapIssue), now)

  // ---- Fetch PRs ----
  const apiPRs = await paginate(page =>
    client.request<any[]>(`/repos/${owner}/${repo}/pulls?state=all&per_page=100&page=${page}`)
  )
  const prMetrics: PRMetrics = analyzePRs(apiPRs.map(mapPR), now)

  // ---- Staleness ----
  const lastCommitDateObj = commitMetrics.lastCommitDate ? new Date(commitMetrics.lastCommitDate) : null
  const lastReleaseDate: Date | null = null // TODO: implement release fetch
  const stalenessMetrics: StalenessMetrics = analyzeStaleness(
    lastCommitDateObj,
    lastReleaseDate,
    issueMetrics.openIssuesCount > 0,
    prMetrics.openPRCount > 0,
    now
  )

  // ---- Score numbers for overall ----
  const commitScore = scoreCommitActivity(commitMetrics)
  const contributorScore = scoreContributorDistribution(contributorMetrics)
  const issueScore = scoreIssueHealth(issueMetrics)
  const prScore = scorePRHealth(prMetrics)
  const stalenessScore = scoreStalenessRisk(stalenessMetrics)

  const overallScore = calculateOverallScore(
    {
      commitActivity: commitScore,
      contributorDistribution: contributorScore,
      issueHealth: issueScore,
      prHealth: prScore,
      stalenessRisk: stalenessScore
    },
    defaultWeights
  )

  return {
    commitMetrics,
    contributorMetrics,
    issueMetrics,
    prMetrics,
    stalenessMetrics,
    overallScore
  }
}
