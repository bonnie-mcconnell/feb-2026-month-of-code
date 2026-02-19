#!/usr/bin/env node
import { program } from "commander"
import { analyzeRepository } from "../index.js"

program
  .name("health-check")
  .argument("<owner/repo>", "GitHub repository to analyze")
  .option("--json", "output JSON")
  .option("--min-score <number>", "exit 1 if score below threshold", parseFloat)
  .option("--token <token>", "GitHub token for authenticated requests")
  .action(
    async (
      repoArg: string,
      opts: {
        token?: string
        json?: boolean
        minScore?: number
      }
    ) => {
      const [owner, repo] = repoArg.split("/")

      if (!owner || !repo) {
        console.error("Invalid repo format. Use owner/repo")
        process.exit(1)
      }

      try {
        const analysisOpts =
          opts.token !== undefined
            ? { owner, repo, token: opts.token }
            : { owner, repo }

        const report = await analyzeRepository(analysisOpts)

        if (opts.json) {
          console.log(JSON.stringify(report, null, 2))
        } else {
          console.log(`Repository Health: ${report.overallScore.toFixed(1)}`)
          console.log(`Commits last 30d: ${report.commitMetrics.commitsLast30Days}`)
          console.log(`Open issues: ${report.issueMetrics.openIssuesCount}`)
          console.log(`Open PRs: ${report.prMetrics.openPRCount}`)
        }

        if (
          opts.minScore !== undefined &&
          report.overallScore < opts.minScore
        ) {
          process.exit(1)
        }

        process.exit(0)
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "Unknown error"
        console.error("Error:", message)
        process.exit(1)
      }
    }
  )

program.parse()
