import { startTracing } from "./infrastructure/observability/tracing";

startTracing("job-worker-service");

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

const app = express();
const port = 3000;

app.use(express.json());

const redis = new Redis({
  host: process.env.REDIS_HOST ?? "localhost",
  port: 6379,
});

const queue = new RedisQueue(redis);
const metrics = new InMemoryMetrics();
const idempotency = new InMemoryIdempotencyStore();
const logger = new ConsoleLogger();
const clock = new RealClock();

const worker = new Worker(
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

let server: ReturnType<typeof app.listen>;

app.get("/health", (_req: Request, res: Response) => {
  res.json({ status: "ok" });
});

app.get("/metrics", (_req: Request, res: Response) => {
  res.type("text/plain");
  res.send(metrics.exportPrometheus());
});

app.post("/enqueue", async (req: Request, res: Response) => {
  const { name, payload, idempotencyKey } = req.body ?? {};

  const job = new Job(
    name ?? "default",
    payload,
    idempotencyKey
  );

  await queue.enqueue(job);

  res.json({ enqueued: job.id });
});

async function start(): Promise<void> {
  await worker.start();

  server = app.listen(port, () => {
    logger.info(`Server running on port ${port}`);
  });
}

async function shutdown(): Promise<void> {
  logger.info("Shutting down...");

  await worker.stop();

  if (server) {
    server.close(() => {
      logger.info("HTTP server closed");
      process.exit(0);
    });
  }
}

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

void start();

export { app };
