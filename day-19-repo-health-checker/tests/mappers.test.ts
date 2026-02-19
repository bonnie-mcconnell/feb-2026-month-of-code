import { describe, it, expect } from "vitest"
import {
  mapCommit,
  mapContributor,
  mapIssue,
  mapPR
} from "../src/github/mappers.js"

describe("mapCommit", () => {
  it("maps commit authoredDate", () => {
    const result = mapCommit({
      commit: { author: { date: "2024-01-01T00:00:00Z" } }
    })

    expect(result.authoredDate.toISOString())
      .toBe("2024-01-01T00:00:00.000Z")
  })
})

describe("mapContributor", () => {
  it("maps login to authorId", () => {
    const result = mapContributor({ login: "alice" })
    expect(result.authorId).toBe("alice")
  })
})

describe("mapIssue", () => {
  it("maps createdAt + closedAt", () => {
    const result = mapIssue({
      created_at: "2024-01-01T00:00:00Z",
      closed_at: null
    })

    expect(result.createdAt instanceof Date).toBe(true)
    expect(result.closedAt).toBeNull()
  })
})

describe("mapPR", () => {
  it("maps PR dates", () => {
    const result = mapPR({
      created_at: "2024-01-01T00:00:00Z",
      merged_at: "2024-01-02T00:00:00Z"
    })

    expect(result.mergedAt instanceof Date).toBe(true)
  })
})
