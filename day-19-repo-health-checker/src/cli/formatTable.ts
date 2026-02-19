import Table from "cli-table3"
import type { RepoHealthReport } from "../index.js"

export function formatReportTable(report: RepoHealthReport): string {
  const table = new Table({
    head: ["Metric", "Score"],
  })

  table.push(
    ["Commit Activity", report.scores.commitActivity],
    ["Contributor Distribution", report.scores.contributorDistribution],
    ["Issue Health", report.scores.issueHealth],
    ["PR Health", report.scores.prHealth],
    ["Staleness Risk", report.scores.stalenessRisk],
    ["Overall", report.overallScore]
  )

  return table.toString()
}
