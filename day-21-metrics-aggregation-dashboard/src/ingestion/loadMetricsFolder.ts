import fs from "node:fs"
import path from "node:path"
import { loadSingleProjectMetrics } from "./loadSingleProjectMetrics"
import { ProjectMetricsBundle } from "../aggregation/multiProjectAggregator"

export function loadMetricsFolder(
  rootFolder: string
): ProjectMetricsBundle[] {

  if (!fs.existsSync(rootFolder)) {
    throw new Error(`Root folder not found: ${rootFolder}`)
  }

  const entries = fs.readdirSync(rootFolder, {
    withFileTypes: true,
  })

  return entries
    .filter((e) => e.isDirectory())
    .map((dir) => {

      const projectPath = path.join(rootFolder, dir.name)

      return {
        projectName: dir.name,
        metrics: loadSingleProjectMetrics(projectPath),
      }
    })
}