import fs from "node:fs"
import { DashboardConfig, validateWeights } from "./config.js"

export function loadConfigFromFile(
  filePath: string
): DashboardConfig {

  const raw = JSON.parse(
    fs.readFileSync(filePath, "utf-8")
  )

  validateWeights(raw.subsystemWeights)

  return raw as DashboardConfig
}