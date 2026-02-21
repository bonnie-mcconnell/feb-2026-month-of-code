import fs from "node:fs"
import path from "node:path"
import { loadSingleProjectMetrics } from "./loadSingleProjectMetrics"

export interface ProjectMetricsBundle {
  projectName: string
  input: ReturnType<typeof loadSingleProjectMetrics>
}

export function loadMetricsFolder(
  rootPath: string
): ProjectMetricsBundle[] {

  if (!fs.existsSync(rootPath)) {
    throw new Error(`Root folder not found: ${rootPath}`)
  }

  const entries = fs.readdirSync(rootPath, {
    withFileTypes: true,
  })

  return entries
    .filter(e => e.isDirectory())
    .map(dir => {
      const fullPath = path.join(rootPath, dir.name)

      return {
        projectName: dir.name,
        input: loadSingleProjectMetrics(fullPath),
      }
    })
}