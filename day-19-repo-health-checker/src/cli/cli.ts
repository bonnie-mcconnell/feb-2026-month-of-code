#!/usr/bin/env node

import { program } from "commander"
import * as fs from "node:fs"

import { analyzeRepository } from "../index.js"
import { validateReport } from "../schema/validateReport.js"
import { formatReportTable } from "./formatTable.js"

import pkg from "../../package.json" with { type: "json" }

program
  .name("repo-health")
  .description("Analyze GitHub repository health and risk")
  .version(pkg.version)

program
  .argument("<owner/repo>", "Repository in owner/repo format")
  .option("--json", "Output JSON")
  .option("--format <type>", "Output format: table|json")
  .option("--min-score <number>", "Fail if score below threshold", parseFloat)
  .option("--token <token>", "GitHub API token")
  .option("--window <days>", "Commit window in days", parseInt)
  .option("--weights <json>", "Custom scoring weights as JSON")
  .option("--trend <months>", "Historical trend mode", parseInt)
  .action(async (repoArg: string, options) => {
    const [owner, repo] = repoArg.split("/")

    if (!owner || !repo) {
      console.error("Invalid repo format. Use owner/repo")
      process.exit(1)
    }

    try {
      const weights =
        typeof options.weights === "string"
          ? JSON.parse(options.weights)
          : undefined

      if (typeof options.trend === "number") {
        const results = await runTrendMode(owner, repo, {
          trend: options.trend,
          token: options.token
        })
        console.log(JSON.stringify(results, null, 2))
        process.exit(0)
      }

      const analysisOptions: any = {
        owner,
        repo
      }

      if (typeof options.token === "string") {
        analysisOptions.token = options.token
      }

      if (typeof options.window === "number") {
        analysisOptions.windowDays = options.window
      }

      if (weights !== undefined) {
        analysisOptions.weights = weights
      }

      const report = await analyzeRepository(analysisOptions)

      validateReport(report)

      if (options.format === "table") {
        console.log(formatReportTable(report))
      } else if (options.json) {
        console.log(JSON.stringify(report, null, 2))
      } else {
        console.log(`\nRepository: ${owner}/${repo}`)
        console.log(`Overall Score: ${report.overallScore.toFixed(1)}`)
        console.log("Metric Scores:", report.scores)

        if (report.riskFlags.length > 0) {
          console.log("\nRisk Flags:")
          for (const flag of report.riskFlags) {
            console.log(`- ${flag}`)
          }
        } else {
          console.log("\nNo major risk flags detected.")
        }
      }

      if (
        typeof options.minScore === "number" &&
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

program
  .command("schema")
  .description("Print JSON schema")
  .action(() => {
    const schema = fs.readFileSync(
      "schema/repo-health.schema.json",
      "utf-8"
    )
    console.log(schema)
  })

program.parse()

async function runTrendMode(
  owner: string,
  repo: string,
  options: {
    trend: number
    token?: string
  }
) {
  const results: { date: string; overallScore: number }[] = []

  for (let i = options.trend; i >= 0; i--) {
    const date = new Date()
    date.setMonth(date.getMonth() - i)

    const analysisOptions: any = {
      owner,
      repo,
      now: date
    }

    if (typeof options.token === "string") {
      analysisOptions.token = options.token
    }

    const report = await analyzeRepository(analysisOptions)

    validateReport(report)

    results.push({
      date: date.toISOString().split("T")[0],
      overallScore: report.overallScore
    })
  }

  return results
}
