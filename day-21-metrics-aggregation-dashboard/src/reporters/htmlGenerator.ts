import { UnifiedMetricsV1 } from "../schema/unifiedMetrics.js"

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

// add heatmap html dashboard

import { MultiProjectDashboard } from "../aggregation/multiProjectAggregator.js"

export function generateHeatmapHtml(
  dashboard: MultiProjectDashboard
): string {

  const rows = dashboard.projects.map((p) => {

    const tier = p.metrics.system.riskTier

    const color =
        tier === "LOW"
            ? "#4CAF50"
            : tier === "MEDIUM"
            ? "#FFC107"
            : "#F44336"

    return `
      <tr>
        <td>${p.projectName}</td>
        <td style="background:${color}">
          ${p.metrics.overallRiskScore.toFixed(1)}
        </td>
        <td>${p.metrics.system.riskTier}</td>
      </tr>
    `
  }).join("")

  return `
  <html>
    <body>
      <h1>Portfolio Risk Dashboard</h1>
      <table border="1">
        <tr>
          <th>Project</th>
          <th>Risk</th>
          <th>Tier</th>
        </tr>
        ${rows}
      </table>
    </body>
  </html>
  `
}