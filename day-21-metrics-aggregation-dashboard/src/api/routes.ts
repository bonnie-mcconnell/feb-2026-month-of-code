import { Router } from "express"
import { aggregateMetrics } from "../aggregation/aggregationEngine"
import { aggregationInputSchema } from "../schema/validation"

export function createRoutes() {
  const router = Router()

  router.get("/health", (_, res) => {
    res.json({ status: "ok" })
  })

  router.post("/aggregate", (req, res) => {

    const parsed = aggregationInputSchema.safeParse(req.body)

    if (!parsed.success) {
      return res.status(400).json({
        error: "Validation failed",
        details: parsed.error.flatten(),
      })
    }

    try {
      const unified = aggregateMetrics(parsed.data)
      res.json(unified)
    } catch (err) {
      res.status(500).json({
        error: "Aggregation failed",
      })
    }
  })

  return router
}