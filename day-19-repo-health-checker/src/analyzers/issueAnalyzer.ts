import type { IssueMetrics } from "../types/metrics.js"

export interface RawIssue {
  createdAt: Date
  closedAt: Date | null
}

const STALE_THRESHOLD_DAYS = 90
const RECENT_WINDOW_DAYS = 90

export function analyzeIssues(
  issues: RawIssue[],
  now: Date = new Date()
): IssueMetrics {
  const openIssues = issues.filter(i => i.closedAt === null)
  const closedIssues = issues.filter(i => i.closedAt !== null)

  const openIssuesCount = openIssues.length

  // ---- Median Open Age ----
  const openAges = openIssues.map(i =>
    diffDays(now, i.createdAt)
  )

  const medianOpenIssueAgeDays =
    openAges.length === 0 ? 0 : median(openAges)

  // ---- Stale Ratio (>90 days) ----
  const staleIssueRatio =
    openIssuesCount === 0
      ? 0
      : openAges.filter(age => age > STALE_THRESHOLD_DAYS).length /
        openIssuesCount

  // ---- Close/Open Ratio (Recent Window) ----
  const recentThreshold = subtractDays(now, RECENT_WINDOW_DAYS)

  const recentClosed = closedIssues.filter(i =>
    i.closedAt !== null && i.closedAt >= recentThreshold
  ).length

  const recentOpened = issues.filter(i =>
    i.createdAt >= recentThreshold
  ).length

  const closeToOpenRatio =
    recentOpened === 0
      ? recentClosed
      : recentClosed / recentOpened

  return {
    openIssuesCount,
    medianOpenIssueAgeDays,
    staleIssueRatio,
    closeToOpenRatio
  }
}

function diffDays(a: Date, b: Date): number {
  return Math.max(
    0,
    Math.floor((a.getTime() - b.getTime()) / (1000 * 60 * 60 * 24))
  )
}

function subtractDays(date: Date, days: number): Date {
  return new Date(date.getTime() - days * 86400000)
}

function median(values: number[]): number {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0
    ? (sorted[mid - 1]! + sorted[mid]!) / 2
    : sorted[mid]!
}
