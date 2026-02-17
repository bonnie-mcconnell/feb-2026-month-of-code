import express from "express";
import { Worker } from "./worker/worker";
import { InMemoryQueue } from "./queue/inMemoryQueue";
import { ExponentialBackoffRetryPolicy } from "./domain/retryPolicy";
import { InMemoryIdempotencyStore } from "./idempotency/inMemoryIdempotencyStore";
import { ConsoleLogger } from "./infrastructure/consoleLogger";
import { InMemoryMetrics } from "./infrastructure/inMemoryMetrics";
import { RealClock } from "./infrastructure/realClock";
import { Job } from "./domain/job";

const app = express();
const port = 3000;

const queue = new InMemoryQueue();
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
  { concurrency: 2, pollIntervalMs: 100, jobTimeoutMs: 5000 }
);

app.get("/health", (_, res) => {
  res.json({ status: "ok" });
});

app.get("/metrics", (_, res) => {
  res.type("text/plain");
  res.send(metrics.exportPrometheus());
});

app.post("/enqueue", express.json(), async (req, res) => {
  const job = new Job(req.body.name ?? "default", req.body.payload);
  await queue.enqueue(job);
  res.json({ enqueued: job.id });
});

async function start() {
  await worker.start();
  app.listen(port, () => {
    logger.info(`Server running on port ${port}`);
  });
}

start();
