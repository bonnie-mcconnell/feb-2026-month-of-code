import { UnifiedMetricsV1 } from "../schema/unifiedMetrics"

export function generateJsonReport(
  metrics: UnifiedMetricsV1
) {
  return {
    exportedAt: new Date().toISOString(),
    metrics,
  }
}