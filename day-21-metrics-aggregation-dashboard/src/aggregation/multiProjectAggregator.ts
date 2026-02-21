import { aggregateMetrics } from "./aggregationEngine"
import { ProjectMetricsBundle } from "../ingestion/loadMetricsFolder"
import { UnifiedMetricsV1 } from "../schema/unifiedMetrics"

export interface MultiProjectDashboard {
  projects: Array<{
    projectName: string
    metrics: UnifiedMetricsV1
  }>
  averageRiskScore: number
}

export function aggregateMultipleProjects(
  bundles: ProjectMetricsBundle[]
): MultiProjectDashboard {

  const projects = bundles.map((bundle) => ({
    projectName: bundle.projectName,
    metrics: aggregateMetrics(bundle),
  }))

  const avgRisk =
    projects.reduce((sum, p) => sum + p.metrics.overallRiskScore, 0) /
    (projects.length || 1)

  return {
    projects,
    averageRiskScore: avgRisk,
  }
}