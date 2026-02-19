export interface GitHubClientOptions {
  token?: string
  fetchImpl?: typeof fetch
  maxRetries?: number
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export class GitHubClient {
  private token: string | undefined
  private fetchImpl: typeof fetch
  private baseUrl = "https://api.github.com"
  private maxRetries: number

  constructor(options: GitHubClientOptions = {}) {
    this.token = options.token
    this.fetchImpl = options.fetchImpl ?? fetch
    this.maxRetries = options.maxRetries ?? 2
  }

  async request<T>(path: string): Promise<T> {
    let attempt = 0

    while (true) {
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

      if (response.ok) {
        return response.json() as Promise<T>
      }

      // Rate limit handling
      if (
        response.status === 403 &&
        response.headers.get("x-ratelimit-remaining") === "0"
      ) {
        const reset = response.headers.get("x-ratelimit-reset")
        if (reset) {
          const resetTime = parseInt(reset, 10) * 1000
          const waitTime = resetTime - Date.now()

          if (waitTime > 0) {
            await sleep(waitTime)
            continue
          }
        }
      }

      // Retry for transient failures
      if (attempt < this.maxRetries && response.status >= 500) {
        const backoff = 2 ** attempt * 500
        await sleep(backoff)
        attempt++
        continue
      }

      throw new Error(`GitHub API error ${response.status}`)
    }
  }
}

export async function fetchLatestRelease(
  client: GitHubClient,
  owner: string,
  repo: string
): Promise<Date | null> {
  try {
    const releases = await client.request<any[]>(
      `/repos/${owner}/${repo}/releases?per_page=1`
    )

    if (!releases || releases.length === 0) {
      return null
    }

    return new Date(releases[0].published_at)
  } catch {
    return null
  }
}
