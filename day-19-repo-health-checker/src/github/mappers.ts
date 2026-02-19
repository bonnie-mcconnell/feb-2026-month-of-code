import type {
  NormalizedCommit,
  NormalizedContributorCommit,
  NormalizedIssue,
  NormalizedPR
} from "../scoring/normalization.js"

/* ================= COMMITS ================= */

export function mapCommit(api: unknown): NormalizedCommit {
  const obj = api as any

  const rawDate = obj?.commit?.author?.date

  return {
    date:
      typeof rawDate === "string"
        ? new Date(rawDate)
        : null
  }
}

/* ================= CONTRIBUTORS ================= */

export function mapContributor(
  api: unknown
): NormalizedContributorCommit {
  const obj = api as any

  return {
    login:
      typeof obj?.login === "string"
        ? obj.login
        : "unknown",
    contributions:
      typeof obj?.contributions === "number"
        ? obj.contributions
        : 0
  }
}

/* ================= ISSUES ================= */

export function mapIssue(api: unknown): NormalizedIssue {
  const obj = api as any

  return {
    createdAt:
      typeof obj?.created_at === "string"
        ? new Date(obj.created_at)
        : new Date(0),
    closedAt:
      typeof obj?.closed_at === "string"
        ? new Date(obj.closed_at)
        : null,
    state:
      typeof obj?.state === "string"
        ? obj.state
        : "unknown"
  }
}

/* ================= PRs ================= */

export function mapPR(api: unknown): NormalizedPR {
  const obj = api as any

  return {
    createdAt:
      typeof obj?.created_at === "string"
        ? new Date(obj.created_at)
        : new Date(0),
    closedAt:
      typeof obj?.closed_at === "string"
        ? new Date(obj.closed_at)
        : null,
    mergedAt:
      typeof obj?.merged_at === "string"
        ? new Date(obj.merged_at)
        : null,
    state:
      typeof obj?.state === "string"
        ? obj.state
        : "unknown"
  }
}
