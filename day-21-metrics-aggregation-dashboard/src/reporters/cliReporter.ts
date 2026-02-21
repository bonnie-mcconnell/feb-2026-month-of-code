import { UnifiedMetricsV1 } from "../schema/unifiedMetrics"

export function renderCliReport(metrics: UnifiedMetricsV1): void {
  console.log("\n==============================")
  console.log("  Metrics Aggregation Report")
  console.log("==============================\n")

  console.log("System")
  console.log("------")
  console.log(`Version: ${metrics.system.version}`)
  console.log(`Generated: ${metrics.system.generatedAt}`)
  console.log("")

  if (metrics.uptime) {
    console.log("Uptime")
    console.log("------")
    console.log(`Availability: ${metrics.uptime.averageAvailabilityPct}%`)
    console.log(`Incidents (30d): ${metrics.uptime.incidentsLast30Days}`)
    console.log(`Uptime Score: ${metrics.uptime.uptimeScore}`)
    console.log("")
  }

  if (metrics.jobs) {
    console.log("Jobs")
    console.log("----")
    console.log(`Failure Rate: ${metrics.jobs.failureRatePct}%`)
    console.log(`Reliability Score: ${metrics.jobs.jobReliabilityScore}`)
    console.log("")
  }

  if (metrics.repository) {
    console.log("Repository")
    console.log("----------")
    console.log(`Complexity: ${metrics.repository.complexityScore}`)
    console.log(`Maintainability: ${metrics.repository.maintainabilityScore}`)
    console.log("")
  }

  if (metrics.repoHealth) {
    console.log("Repo Health")
    console.log("-----------")
    console.log(`Health Score: ${metrics.repoHealth.healthScore}`)
    console.log(`Activity Score: ${metrics.repoHealth.activityScore}`)
    console.log("")
  }

  console.log("Overall")
  console.log("-------")
  console.log(`Risk Score: ${metrics.overallRiskScore}`)
  console.log(`Health Score: ${metrics.overallHealthScore}`)
  console.log("")
}