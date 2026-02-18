export interface GitHubClientOptions {
  token?: string
  fetchImpl?: typeof fetch
}

export class GitHubClient {
  private token: string | undefined
  private fetchImpl: typeof fetch
  private baseUrl = "https://api.github.com"

  constructor(options: GitHubClientOptions = {}) {
    this.token = options.token // now matches string | undefined exactly
    this.fetchImpl = options.fetchImpl ?? fetch
  }

  async request<T>(path: string): Promise<T> {
    const headers: Record<string, string> = {
      Accept: "application/vnd.github+json"
    }

    if (this.token !== undefined) {
      headers["Authorization"] = `Bearer ${this.token}`
    }

    const response = await this.fetchImpl(
      `${this.baseUrl}${path}`,
      { headers }
    )

    if (!response.ok) {
      throw new Error(`GitHub API error ${response.status}`)
    }

    return response.json() as Promise<T>
  }
}
