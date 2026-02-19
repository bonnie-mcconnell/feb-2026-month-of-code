#!/usr/bin/env node

import { program } from "commander"
import * as fs from "node:fs"
import * as path from "node:path"
import { fileURLToPath } from "node:url"

import { analyzeRepository } from "../index.js"
import type { RepoAnalysisOptions } from "../index.js"
import { validateReport } from "../schema/validateReport.js"
import { formatReportTable } from "./formatTable.js"

import pkg from "../../package.json" with { type: "json" }

/* -------------------------------------------------------------------------- */
/*                                  Root CLI                                  */
/* -------------------------------------------------------------------------- */

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
  .option("--graphql", "Use GraphQL API")
  .option("--no-cache", "Disable cache")
  .option("--output <file>", "Write output to file")
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

      /* ----------------------------- Trend Mode ----------------------------- */

      if (typeof options.trend === "number") {
        const results = await runTrendMode(owner, repo, {
          trend: options.trend,
          token: options.token,
          windowDays: options.window,
          graphql: options.graphql,
          noCache: options.noCache
        })

        const trendOutput = JSON.stringify(results, null, 2)

        if (options.output) {
          fs.writeFileSync(options.output, trendOutput)
        } else {
          console.log(trendOutput)
        }

        process.exit(0)
      }

      /* --------------------------- Normal Analysis -------------------------- */

      const analysisOptions: RepoAnalysisOptions = {
        owner,
        repo,
        ...(typeof options.token === "string" && { token: options.token }),
        ...(typeof options.window === "number" && {
          windowDays: options.window
        }),
        ...(weights !== undefined && { weights }),
        ...(options.graphql && { graphql: true }),
        ...(options.noCache && { noCache: true })
      }

      const report = await analyzeRepository(analysisOptions)

      validateReport(report)

      let output: string

      if (options.format === "table") {
        output = formatReportTable(report)
      } else if (options.json || options.format === "json") {
        output = JSON.stringify(report, null, 2)
      } else {
        output = [
          `\nRepository: ${owner}/${repo}`,
          `Overall Score: ${report.overallScore.toFixed(1)}`,
          `Metric Scores: ${JSON.stringify(report.scores, null, 2)}`,
          report.riskFlags.length > 0
            ? `\nRisk Flags:\n- ${report.riskFlags.join("\n- ")}`
            : "\nNo major risk flags detected."
        ].join("\n")
      }

      if (options.output) {
        fs.writeFileSync(options.output, output)
      } else {
        console.log(output)
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

/* -------------------------------------------------------------------------- */
/*                                  Compare                                   */
/* -------------------------------------------------------------------------- */

program
  .command("compare <repoA> <repoB>")
  .description("Compare two repositories")
  .option("--token <token>", "GitHub API token")
  .option("--window <days>", "Commit window in days", parseInt)
  .option("--graphql", "Use GraphQL API")
  .option("--no-cache", "Disable cache")
  .action(async (repoA: string, repoB: string, options) => {
    const [ownerA, nameA] = repoA.split("/")
    const [ownerB, nameB] = repoB.split("/")

    if (!ownerA || !nameA || !ownerB || !nameB) {
      console.error("Invalid repo format. Use owner/repo")
      process.exit(1)
    }

    try {
      const sharedOptions: Partial<RepoAnalysisOptions> = {
        ...(typeof options.token === "string" && { token: options.token }),
        ...(typeof options.window === "number" && {
          windowDays: options.window
        }),
        ...(options.graphql && { graphql: true }),
        ...(options.noCache && { noCache: true })
      }

      const reportA = await analyzeRepository({
        owner: ownerA,
        repo: nameA,
        ...sharedOptions
      })

      const reportB = await analyzeRepository({
        owner: ownerB,
        repo: nameB,
        ...sharedOptions
      })

      validateReport(reportA)
      validateReport(reportB)

      console.log(
        JSON.stringify(
          {
            [repoA]: reportA.overallScore,
            [repoB]: reportB.overallScore
          },
          null,
          2
        )
      )

      process.exit(0)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unknown error"
      console.error("Error:", message)
      process.exit(1)
    }
  })

/* -------------------------------------------------------------------------- */
/*                                   Schema                                   */
/* -------------------------------------------------------------------------- */

program
  .command("schema")
  .description("Print JSON schema")
  .option("--schema-file <file>", "Write JSON schema to file")
  .action((options) => {
    try {
      const __filename = fileURLToPath(import.meta.url)
      const __dirname = path.dirname(__filename)

      const schemaPath = path.resolve(
        __dirname,
        "../schema/repo-health.schema.json"
      )

      const schema = fs.readFileSync(schemaPath, "utf-8")

      if (options.schemaFile) {
        fs.writeFileSync(options.schemaFile, schema)
      } else {
        console.log(schema)
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

/* -------------------------------------------------------------------------- */
/*                                Trend Engine                                */
/* -------------------------------------------------------------------------- */

async function runTrendMode(
  owner: string,
  repo: string,
  options: {
    trend: number
    token?: string
    windowDays?: number
    graphql?: boolean
    noCache?: boolean
  }
): Promise<{ date: string; overallScore: number }[]> {
  const results: { date: string; overallScore: number }[] = []

  for (let i = options.trend; i >= 0; i--) {
    const date = new Date()
    date.setMonth(date.getMonth() - i)

    const report = await analyzeRepository({
      owner,
      repo,
      now: date,
      ...(typeof options.token === "string" && {
        token: options.token
      }),
      ...(typeof options.windowDays === "number" && {
        windowDays: options.windowDays
      }),
      ...(options.graphql && { graphql: true }),
      ...(options.noCache && { noCache: true })
    })

    validateReport(report)

    results.push({
      date: date.toISOString().slice(0, 10),
      overallScore: report.overallScore
    })
  }

  return results
}
