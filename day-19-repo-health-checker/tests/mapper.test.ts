import { describe, it, expect } from "vitest"
import {
  mapCommit,
  mapContributor,
  mapIssue,
  mapPR
} from "../src/github/mappers.js"

describe("mapCommit", () => {
  it("parses valid commit date", () => {
    const input = {
      commit: {
        author: { date: "2024-01-01T00:00:00Z" }
      }
    }

    const result = mapCommit(input)
    expect(result.date?.toISOString()).toBe("2024-01-01T00:00:00.000Z")
  })

  it("returns null for invalid date", () => {
    const result = mapCommit({})
    expect(result.date).toBeNull()
  })
})

describe("mapContributor", () => {
  it("maps valid contributor", () => {
    const result = mapContributor({
      login: "alice",
      contributions: 42
    })

    expect(result.login).toBe("alice")
    expect(result.contributions).toBe(42)
  })

  it("defaults invalid values", () => {
    const result = mapContributor({})
    expect(result.login).toBe("unknown")
    expect(result.contributions).toBe(0)
  })
})

describe("mapIssue", () => {
  it("maps issue correctly", () => {
    const result = mapIssue({
      created_at: "2024-01-01T00:00:00Z",
      closed_at: null,
      state: "open"
    })

    expect(result.createdAt instanceof Date).toBe(true)
    expect(result.closedAt).toBeNull()
    expect(result.state).toBe("open")
  })
})

describe("mapPR", () => {
  it("maps PR correctly", () => {
    const result = mapPR({
      created_at: "2024-01-01T00:00:00Z",
      merged_at: "2024-01-02T00:00:00Z",
      state: "closed"
    })

    expect(result.mergedAt instanceof Date).toBe(true)
    expect(result.state).toBe("closed")
  })
})
