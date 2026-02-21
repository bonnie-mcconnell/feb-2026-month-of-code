import { UnifiedMetricsV1 } from "../schema/unifiedMetrics.js"

export function generateJsonReport(
  metrics: UnifiedMetricsV1
) {
  return {
    exportedAt: new Date().toISOString(),
    metrics,
  }
}