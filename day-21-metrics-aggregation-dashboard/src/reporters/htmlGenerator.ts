import { UnifiedMetricsV1 } from "../schema/unifiedMetrics"

export function generateHtmlReport(
  metrics: UnifiedMetricsV1
): string {

  return `
  <!DOCTYPE html>
  <html>
  <head>
    <title>Unified Metrics Report</title>
    <style>
      body { font-family: Arial; padding: 40px; }
      h1 { margin-bottom: 10px; }
      .section { margin-bottom: 30px; }
      .card { padding: 15px; border: 1px solid #ccc; border-radius: 6px; }
      .risk { font-weight: bold; }
    </style>
  </head>
  <body>
    <h1>Unified Metrics Report</h1>

    <div class="section card">
      <h2>Overall</h2>
      <p class="risk">Risk Score: ${metrics.overallRiskScore}</p>
      <p>Health Score: ${metrics.overallHealthScore}</p>
    </div>

    ${
      metrics.uptime
        ? `
        <div class="section card">
          <h2>Uptime</h2>
          <p>Availability: ${metrics.uptime.averageAvailabilityPct}%</p>
          <p>Incidents (30d): ${metrics.uptime.incidentsLast30Days}</p>
          <p>Score: ${metrics.uptime.uptimeScore}</p>
        </div>`
        : ""
    }

    ${
      metrics.jobs
        ? `
        <div class="section card">
          <h2>Jobs</h2>
          <p>Failure Rate: ${metrics.jobs.failureRatePct}%</p>
          <p>Reliability Score: ${metrics.jobs.jobReliabilityScore}</p>
        </div>`
        : ""
    }

  </body>
  </html>
  `
}