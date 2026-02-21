import express from "express"
import { createRoutes } from "./routes"

export function startServer(port = 3000) {

  const app = express()

  app.use(express.json())
  app.use("/api", createRoutes())

  app.listen(port, () => {
    console.log(
      `Metrics API running on http://localhost:${port}`
    )
  })
}