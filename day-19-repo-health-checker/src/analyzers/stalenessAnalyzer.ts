import type { StalenessMetrics } from "../types/metrics.js"

export function analyzeStaleness(
  lastCommitDate: Date | null,
  lastReleaseDate: Date | null,
  recentIssueActivity: boolean,
  recentPRActivity: boolean,
  now: Date = new Date()
): StalenessMetrics {
  return {
    daysSinceLastCommit:
      lastCommitDate === null
        ? 999
        : diffDays(now, lastCommitDate),

    daysSinceLastRelease:
      lastReleaseDate === null
        ? null
        : diffDays(now, lastReleaseDate),

    recentIssueActivity,
    recentPRActivity
  }
}

function diffDays(a: Date, b: Date): number {
  return Math.max(
    0,
    Math.floor((a.getTime() - b.getTime()) / 86400000)
  )
}
