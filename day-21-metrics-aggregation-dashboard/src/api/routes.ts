import { Router } from "express"
import { z } from "zod"

import { aggregateMetrics } from "../aggregation/aggregationEngine.js"
import { aggregateMultipleProjects } from "../aggregation/multiProjectAggregator.js"
import { loadMetricsFolder } from "../ingestion/loadMetricsFolder.js"
import { aggregationInputSchema } from "../schema/validation.js"

export function createRoutes() {

  const router = Router()

  router.get("/health", (_, res) => {
    res.json({ status: "ok" })
  })

  router.post("/aggregate", (req, res) => {

    const parsed = aggregationInputSchema.safeParse(req.body)

    if (!parsed.success) {
      return res.status(400).json(parsed.error.flatten())
    }

    const result = aggregateMetrics(parsed.data)
    res.json(result)
  })

  const multiSchema = z.object({
    folder: z.string().min(1),
  })

  router.get("/multi-project", (req, res) => {

    const parsed = multiSchema.safeParse(req.query)

    if (!parsed.success) {
      return res.status(400).json(parsed.error.flatten())
    }

    const bundles = loadMetricsFolder(parsed.data.folder)
    const dashboard = aggregateMultipleProjects(bundles)

    res.json(dashboard)
  })

  return router
}