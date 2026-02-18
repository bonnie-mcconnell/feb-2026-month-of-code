import type { PRMetrics } from "../types/metrics.js"

export interface RawPR {
  createdAt: Date
  closedAt: Date | null
  mergedAt: Date | null
}

const STALE_THRESHOLD_DAYS = 30

export function analyzePRs(
  prs: RawPR[],
  now: Date = new Date()
): PRMetrics {
  const openPRs = prs.filter(pr => pr.closedAt === null)
  const closedPRs = prs.filter(pr => pr.closedAt !== null)
  const mergedPRs = prs.filter(pr => pr.mergedAt !== null)

  const openPRCount = openPRs.length

  // ---- Merge Ratio ----
  const mergeRatio =
    closedPRs.length === 0
      ? 0
      : mergedPRs.length / closedPRs.length

  // ---- Stale PR Ratio ----
  const stalePRRatio =
    openPRCount === 0
      ? 0
      : openPRs.filter(pr =>
          diffDays(now, pr.createdAt) > STALE_THRESHOLD_DAYS
        ).length / openPRCount

  // ---- Avg Time To Merge ----
  const mergeDurations = mergedPRs.map(pr =>
    diffDays(pr.mergedAt!, pr.createdAt)
  )

  const avgTimeToMergeDays =
    mergeDurations.length === 0
      ? 0
      : mergeDurations.reduce((a, b) => a + b, 0) /
        mergeDurations.length

  return {
    openPRCount,
    avgTimeToMergeDays,
    mergeRatio,
    stalePRRatio
  }
}

function diffDays(a: Date, b: Date): number {
  return Math.max(
    0,
    Math.floor((a.getTime() - b.getTime()) / 86400000)
  )
}
