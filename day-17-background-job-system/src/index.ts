import { InMemoryQueue } from "./queue/inMemoryQueue";
import { ExponentialBackoffRetryPolicy } from "./domain/retryPolicy";
import { InMemoryIdempotencyStore } from "./idempotency/inMemoryIdempotencyStore";
import { ConsoleLogger } from "./infrastructure/consoleLogger";
import { InMemoryMetrics } from "./infrastructure/inMemoryMetrics";
import { RealClock } from "./infrastructure/realClock";
import { Worker } from "./worker/worker";
import { WorkerLifecycle } from "./worker/lifecycle";
import { Job } from "./domain/job";

async function main() {
  const queue = new InMemoryQueue();
  const metrics = new InMemoryMetrics();
  const worker = new Worker(
    queue,
    {
      async process(job: Job) {
        console.log("Processing:", job.id);
      },
    },
    new ExponentialBackoffRetryPolicy(3, 100),
    new InMemoryIdempotencyStore(),
    new ConsoleLogger(),
    metrics,
    new RealClock(),
    { concurrency: 2, pollIntervalMs: 100, jobTimeoutMs: 5000 }
  );

  const lifecycle = new WorkerLifecycle(worker, new ConsoleLogger());
  lifecycle.attachSignalHandlers();

  await lifecycle.start();

  await queue.enqueue(new Job("demo"));
}

main();
