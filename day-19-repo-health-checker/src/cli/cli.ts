#!/usr/bin/env node
import { program } from "commander"
import { analyzeRepository } from "../index.js"
import pkg from "../../package.json" with { type: "json" }

program
  .name("repo-health")
  .description("Analyze GitHub repository health and risk")
  .version(pkg.version)

program
  .argument("<owner/repo>", "Repository in owner/repo format")
  .option("--json", "Output JSON")
  .option("--min-score <number>", "Fail if score below threshold", parseFloat)
  .option("--token <token>", "GitHub API token")
  .option("--window <days>", "Commit window in days", parseInt)
  .option("--weights <json>", "Custom scoring weights as JSON")
  .action(async (repoArg, options) => {
    const [owner, repo] = repoArg.split("/")

    if (!owner || !repo) {
      console.error("Invalid repo format. Use owner/repo")
      process.exit(1)
    }

    try {
      const weights =
        options.weights !== undefined
          ? JSON.parse(options.weights)
          : undefined

      const report = await analyzeRepository({
        owner,
        repo,
        token: options.token,
        windowDays: options.window,
        weights
      })

      if (options.json) {
        console.log(JSON.stringify(report, null, 2))
      } else {
        console.log(`\nRepository: ${owner}/${repo}`)
        console.log(`Overall Score: ${report.overallScore.toFixed(1)}`)
        console.log("Metric Scores:", report.scores)

        if (report.riskFlags.length > 0) {
          console.log("\nRisk Flags:")
          for (const flag of report.riskFlags) {
            console.log(`- ${flag.code}: ${flag.message}`)
          }
        } else {
          console.log("\nNo major risk flags detected.")
        }
      }

      if (
        options.minScore !== undefined &&
        report.overallScore < options.minScore
      ) {
        process.exit(1)
      }

      process.exit(0)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unknown error"
      console.error("Error:", message)
      process.exit(1)
    }
  })

program.parse()
