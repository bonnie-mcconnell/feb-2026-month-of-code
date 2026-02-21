import { UnifiedMetricsV1 } from "../schema/unifiedMetrics"

export interface HistoricalComparison {
  deltaRisk: number
  improved: boolean
}

export function compareSnapshots(
  previous: UnifiedMetricsV1,
  current: UnifiedMetricsV1
): HistoricalComparison {

  const delta = current.overallRiskScore - previous.overallRiskScore

  return {
    deltaRisk: delta,
    improved: delta < 0,
  }
}