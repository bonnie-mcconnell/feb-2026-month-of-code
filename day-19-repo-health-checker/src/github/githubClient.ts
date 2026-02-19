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
  private readonly baseUrl = "https://api.github.com"
  private readonly maxRetries: number

  constructor(options: GitHubClientOptions = {}) {
    this.token = options.token
    this.fetchImpl = options.fetchImpl ?? fetch
    this.maxRetries = options.maxRetries ?? 2
  }

  /* ================= REST ================= */

  async request<T>(path: string): Promise<T> {
    let attempt = 0

    while (true) {
      const headers: Record<string, string> = {
        Accept: "application/vnd.github+json"
      }

      if (typeof this.token === "string") {
        headers.Authorization = `Bearer ${this.token}`
      }

      const response = await this.fetchImpl(
        `${this.baseUrl}${path}`,
        { headers }
      )

      if (response.ok) {
        return response.json() as Promise<T>
      }

      if (
        response.status === 403 &&
        response.headers.get("x-ratelimit-remaining") === "0"
      ) {
        const reset = response.headers.get("x-ratelimit-reset")
        if (reset) {
          const waitTime =
            parseInt(reset, 10) * 1000 - Date.now()

          if (waitTime > 0) {
            await sleep(waitTime)
            continue
          }
        }
      }

      if (attempt < this.maxRetries && response.status >= 500) {
        await sleep(2 ** attempt * 500)
        attempt++
        continue
      }

      throw new Error(`GitHub API error ${response.status}`)
    }
  }

  /* ================= GRAPHQL ================= */

  async graphql<T>(
    query: string,
    variables?: Record<string, unknown>
  ): Promise<T> {
    if (typeof this.token !== "string") {
      throw new Error("GraphQL requires authentication token")
    }

    const response = await this.fetchImpl(
      `${this.baseUrl}/graphql`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.token}`
        },
        body: JSON.stringify({ query, variables })
      }
    )

    if (!response.ok) {
      throw new Error(
        `GitHub GraphQL error ${response.status}`
      )
    }

    const json = await response.json()

    if (json?.errors) {
      throw new Error(
        json.errors
          .map((e: { message: string }) => e.message)
          .join(", ")
      )
    }

    return json.data as T
  }
}

/* ================= HELPERS ================= */

export async function fetchLatestRelease(
  client: GitHubClient,
  owner: string,
  repo: string
): Promise<Date | null> {
  try {
    const releases = await client.request<
      { published_at: string }[]
    >(`/repos/${owner}/${repo}/releases?per_page=1`)

    const first = releases[0]
    if (!first) return null

    return new Date(first.published_at)
  } catch {
    return null
  }
}
