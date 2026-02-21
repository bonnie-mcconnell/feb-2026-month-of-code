import { aggregateMetrics } from "./aggregationEngine"
import { AggregationInput } from "./aggregationEngine"
import { UnifiedMetricsV1 } from "../schema/unifiedMetrics"
import { DashboardConfig } from "../config/config"

export interface ProjectMetricsBundle {
  projectName: string
  metrics: AggregationInput
}

export interface MultiProjectDashboard {
  projects: Array<{
    projectName: string
    metrics: UnifiedMetricsV1
  }>
  averageRiskScore: number
}

export function aggregateMultipleProjects(
  bundles: ProjectMetricsBundle[],
  config?: DashboardConfig
): MultiProjectDashboard {

  const projects = bundles.map((bundle) => ({
    projectName: bundle.projectName,
    metrics: aggregateMetrics({
      ...bundle.metrics,
      config
    }),
  }))

  const avgRisk =
    projects.reduce((sum, p) => sum + p.metrics.overallRiskScore, 0) /
    (projects.length || 1)

  return {
    projects,
    averageRiskScore: avgRisk,
  }
}