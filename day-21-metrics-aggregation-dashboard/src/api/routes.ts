import { Router } from "express"
import { aggregateMetrics } from "../aggregation/aggregationEngine"

export function createRoutes() {
  const router = Router()

  router.get("/health", (_, res) => {
    res.json({ status: "ok" })
  })

  router.post("/aggregate", (req, res) => {
    try {
      const unified = aggregateMetrics(req.body)
      res.json(unified)
    } catch (err) {
      res.status(400).json({ error: "Invalid input" })
    }
  })

  return router
}