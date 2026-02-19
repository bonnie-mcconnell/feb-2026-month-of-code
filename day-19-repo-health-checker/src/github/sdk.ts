import { GitHubClient } from "./githubClient.js"

export interface GitHubCommit {
  sha: string
  commit: {
    author: {
      date: string
    }
  }
}

export interface GitHubContributor {
  login: string
  contributions: number
}

export interface GitHubIssue {
  created_at: string
  closed_at: string | null
  state: "open" | "closed"
  pull_request?: unknown
}

export interface GitHubPR {
  created_at: string
  merged_at: string | null
  closed_at: string | null
  state: "open" | "closed"
}

export class GitHubSDK {
  constructor(private client: GitHubClient) {}

  async getCommits(owner: string, repo: string, page: number) {
    return this.client.request<GitHubCommit[]>(
      `/repos/${owner}/${repo}/commits?per_page=100&page=${page}`
    )
  }

  async getContributors(owner: string, repo: string, page: number) {
    return this.client.request<GitHubContributor[]>(
      `/repos/${owner}/${repo}/contributors?per_page=100&page=${page}`
    )
  }

  async getIssues(owner: string, repo: string, page: number) {
    return this.client.request<GitHubIssue[]>(
      `/repos/${owner}/${repo}/issues?state=all&per_page=100&page=${page}`
    )
  }

  async getPRs(owner: string, repo: string, page: number) {
    return this.client.request<GitHubPR[]>(
      `/repos/${owner}/${repo}/pulls?state=all&per_page=100&page=${page}`
    )
  }
}
