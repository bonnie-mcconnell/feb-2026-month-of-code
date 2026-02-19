/* ================= TYPE IMPORTS ================= */

import type { NormalizedCommit } from "../analyzers/commitAnalyzer.js"
import type { NormalizedContributorCommit } from "../analyzers/contributorAnalyzer.js"
import type { RawIssue } from "../analyzers/issueAnalyzer.js"
import type { RawPR } from "../analyzers/prAnalyzer.js"

/* ================= INTERNAL HELPERS ================= */

function parseDate(value: unknown): Date | null {
  if (typeof value !== "string") return null
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? null : d
}

function parseDateOrEpoch(value: unknown): Date {
  const parsed = parseDate(value)
  return parsed ?? new Date(0)
}

/* ================= COMMITS ================= */

export function mapCommit(api: unknown): NormalizedCommit {
  if (typeof api !== "object" || api === null) {
    return { authoredDate: new Date(0) }
  }

  const obj = api as {
    commit?: {
      author?: {
        date?: unknown
      }
    }
  }

  return {
    authoredDate: parseDateOrEpoch(obj.commit?.author?.date)
  }
}

/* ================= CONTRIBUTORS ================= */

export function mapContributor(
  api: unknown
): NormalizedContributorCommit {
  if (typeof api !== "object" || api === null) {
    return { authorId: "unknown" }
  }

  const obj = api as {
    login?: unknown
  }

  return {
    authorId:
      typeof obj.login === "string" && obj.login.length > 0
        ? obj.login
        : "unknown"
  }
}

/* ================= ISSUES ================= */

export function mapIssue(api: unknown): RawIssue {
  if (typeof api !== "object" || api === null) {
    return {
      createdAt: new Date(0),
      closedAt: null
    }
  }

  const obj = api as {
    created_at?: unknown
    closed_at?: unknown
  }

  return {
    createdAt: parseDateOrEpoch(obj.created_at),
    closedAt: parseDate(obj.closed_at)
  }
}

/* ================= PRs ================= */

export function mapPR(api: unknown): RawPR {
  if (typeof api !== "object" || api === null) {
    return {
      createdAt: new Date(0),
      closedAt: null,
      mergedAt: null
    }
  }

  const obj = api as {
    created_at?: unknown
    closed_at?: unknown
    merged_at?: unknown
  }

  return {
    createdAt: parseDateOrEpoch(obj.created_at),
    closedAt: parseDate(obj.closed_at),
    mergedAt: parseDate(obj.merged_at)
  }
}
