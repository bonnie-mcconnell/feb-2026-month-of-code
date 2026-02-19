import { GitHubClient } from "./githubClient.js"

export interface GraphQLRepoStats {
  stars: number
  forks: number
  openIssues: number
  watchers: number
  pushedAt: string
}

export async function fetchRepoStatsGraphQL(
  client: GitHubClient,
  owner: string,
  repo: string
): Promise<GraphQLRepoStats> {
  const data = await client.graphql<{
    repository: {
      stargazerCount: number
      forkCount: number
      issues: { totalCount: number }
      watchers: { totalCount: number }
      pushedAt: string
    }
  }>(
    `
    query ($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        stargazerCount
        forkCount
        pushedAt
        watchers { totalCount }
        issues(states: OPEN) { totalCount }
      }
    }
    `,
    { owner, repo }
  )

  return {
    stars: data.repository.stargazerCount,
    forks: data.repository.forkCount,
    openIssues: data.repository.issues.totalCount,
    watchers: data.repository.watchers.totalCount,
    pushedAt: data.repository.pushedAt
  }
}
