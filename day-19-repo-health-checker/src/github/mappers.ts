import type { RawIssue } from "../analyzers/issueAnalyzer.js"
import type { RawPR } from "../analyzers/prAnalyzer.js"

export function mapIssue(apiIssue: any): RawIssue {
  return {
    createdAt: new Date(apiIssue.created_at),
    closedAt: apiIssue.closed_at
      ? new Date(apiIssue.closed_at)
      : null
  }
}

export function mapPR(apiPR: any): RawPR {
  return {
    createdAt: new Date(apiPR.created_at),
    closedAt: apiPR.closed_at
      ? new Date(apiPR.closed_at)
      : null,
    mergedAt: apiPR.merged_at
      ? new Date(apiPR.merged_at)
      : null
  }
}
