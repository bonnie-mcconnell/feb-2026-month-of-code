import { describe, it, expect } from "vitest"
import { GitHubClient } from "../src/github/githubClient.js"

describe("GitHubClient", () => {
  it("throws on GraphQL without token", async () => {
    const client = new GitHubClient()

    await expect(
      client.graphql("query { viewer { login } }")
    ).rejects.toThrow()
  })
})
