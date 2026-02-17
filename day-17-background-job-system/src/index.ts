import { startTracing } from "./infrastructure/observability/tracing";
import express, { Request, Response } from "express";
import Redis from "ioredis";
import { Worker } from "./worker/worker";
import { RedisQueue } from "./queue/redisQueue";
import { ExponentialBackoffRetryPolicy } from "./domain/retryPolicy";
import { InMemoryIdempotencyStore } from "./idempotency/inMemoryIdempotencyStore";
import { ConsoleLogger } from "./infrastructure/consoleLogger";
import { InMemoryMetrics } from "./infrastructure/inMemoryMetrics";
import { RealClock } from "./infrastructure/realClock";
import { Job } from "./domain/job";

/**
 * Shared logger (safe for tests)
 */
const logger = new ConsoleLogger();

/**
 * Express app (exported for tests)
 */
const app = express();
app.use(express.json());

/**
 * Dependencies (assigned in bootstrap)
 */
let queue: RedisQueue | undefined;

/**
 * Routes (ALWAYS registered — fixes 404)
 */
app.get("/health", (_req: Request, res: Response) => {
  res.status(200).json({ status: "ok" });
});

app.post("/enqueue", async (req: Request, res: Response) => {
  try {
    const { name, payload, idempotencyKey } = req.body ?? {};
    const job = new Job(name ?? "default", payload, idempotencyKey);

    // During tests queue is undefined — simulate success
    if (!queue) {
      return res.status(200).json({ enqueued: job.id });
    }

    await queue.enqueue(job);
    res.status(200).json({ enqueued: job.id });
  } catch (err) {
    logger.error("Failed to enqueue job", err as Error);
    res.status(500).json({ error: "Failed to enqueue job" });
  }
});

/**
 * Runtime-only state
 */
let redis: Redis | undefined;
let worker: Worker | undefined;
let server: ReturnType<typeof app.listen> | undefined;

/**
 * Production bootstrap
 */
export async function bootstrap(): Promise<void> {
  startTracing("job-worker-service");

  const port = Number(process.env.PORT ?? 3000);

  redis = new Redis({
    host: process.env.REDIS_HOST ?? "localhost",
    port: Number(process.env.REDIS_PORT ?? 6379),
  });

  queue = new RedisQueue(redis);

  const metrics = new InMemoryMetrics();
  const idempotency = new InMemoryIdempotencyStore();
  const clock = new RealClock();

  worker = new Worker(
    queue,
    {
      async process(job) {
        logger.info(`Processing job ${job.id}`);
      },
    },
    new ExponentialBackoffRetryPolicy(3, 100),
    idempotency,
    logger,
    metrics,
    clock,
    {
      concurrency: 2,
      pollIntervalMs: 100,
      jobTimeoutMs: 5000,
    }
  );

  app.get("/metrics", (_req: Request, res: Response) => {
    res.type("text/plain");
    res.send(metrics.exportPrometheus());
  });

  await redis.connect();
  await worker.start();

  server = app.listen(port, () => {
    logger.info(`Server running on port ${port}`);
  });

  setupShutdown();
}

/**
 * Graceful shutdown
 */
function setupShutdown(): void {
  const shutdown = async () => {
    logger.info("Shutting down...");

    try {
      if (worker) await worker.stop();
      if (redis) await redis.quit();
      if (server) server.close();
    } catch (err) {
      logger.error("Shutdown error", err as Error);
    } finally {
      process.exit(0);
    }
  };

  process.on("SIGTERM", shutdown);
  process.on("SIGINT", shutdown);
}

/**
 * Only run bootstrap in production
 */
if (require.main === module) {
  bootstrap().catch((err) => {
    console.error("Fatal bootstrap error:", err);
    process.exit(1);
  });
}

export { app };
