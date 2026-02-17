import { Worker } from "../worker/worker";
import { InMemoryQueue } from "../queue/inMemoryQueue";
import { ExponentialBackoffRetryPolicy } from "../domain/retryPolicy";
import { InMemoryIdempotencyStore } from "../idempotency/inMemoryIdempotencyStore";
import { ConsoleLogger } from "../infrastructure/consoleLogger";
import { InMemoryMetrics } from "../infrastructure/inMemoryMetrics";
import { RealClock } from "../infrastructure/realClock";
import { Job } from "../domain/job";

describe("Worker", () => {
  let queue: InMemoryQueue;
  let metrics: InMemoryMetrics;
  let idempotency: InMemoryIdempotencyStore;
  let logger: ConsoleLogger;
  let clock: RealClock;

  beforeEach(() => {
    queue = new InMemoryQueue();
    metrics = new InMemoryMetrics();
    idempotency = new InMemoryIdempotencyStore();
    logger = new ConsoleLogger();
    clock = new RealClock();
  });

  test("processes a job successfully", async () => {
    const processor = {
      process: jest.fn().mockResolvedValue(undefined),
    };

    const worker = new Worker(
      queue,
      processor,
      new ExponentialBackoffRetryPolicy(3, 10),
      idempotency,
      logger,
      metrics,
      clock,
      { concurrency: 1, pollIntervalMs: 10, jobTimeoutMs: 1000 }
    );

    const job = new Job("test");
    await queue.enqueue(job);

    await worker.start();
    await new Promise((r) => setTimeout(r, 50));
    await worker.stop();

    expect(processor.process).toHaveBeenCalled();
    expect(metrics.getCounter("jobs_completed_total")).toBe(1);
  });

  test("skips idempotent job", async () => {
    const processor = {
      process: jest.fn(),
    };

    const worker = new Worker(
      queue,
      processor,
      new ExponentialBackoffRetryPolicy(3, 10),
      idempotency,
      logger,
      metrics,
      clock,
      { concurrency: 1, pollIntervalMs: 10, jobTimeoutMs: 1000 }
    );

    const job = new Job("test", undefined, "key1");

    await idempotency.markProcessed("key1");
    await queue.enqueue(job);

    await worker.start();
    await new Promise((r) => setTimeout(r, 50));
    await worker.stop();

    expect(processor.process).not.toHaveBeenCalled();
    expect(metrics.getCounter("jobs_skipped_idempotent")).toBe(1);
  });

  test("retries failed job", async () => {
    const processor = {
      process: jest
        .fn()
        .mockRejectedValueOnce(new Error("fail"))
        .mockResolvedValueOnce(undefined),
    };

    const worker = new Worker(
      queue,
      processor,
      new ExponentialBackoffRetryPolicy(3, 10),
      idempotency,
      logger,
      metrics,
      clock,
      { concurrency: 1, pollIntervalMs: 10, jobTimeoutMs: 1000 }
    );

    const job = new Job("test");
    await queue.enqueue(job);

    await worker.start();
    await new Promise((r) => setTimeout(r, 200));
    await worker.stop();

    expect(processor.process).toHaveBeenCalledTimes(2);
    expect(metrics.getCounter("jobs_retried_total")).toBe(1);
  });

  test("dead letters after max retries", async () => {
    const processor = {
      process: jest.fn().mockRejectedValue(new Error("fail")),
    };

    const worker = new Worker(
      queue,
      processor,
      new ExponentialBackoffRetryPolicy(1, 10),
      idempotency,
      logger,
      metrics,
      clock,
      { concurrency: 1, pollIntervalMs: 10, jobTimeoutMs: 1000 }
    );

    const job = new Job("test");
    await queue.enqueue(job);

    await worker.start();
    await new Promise((r) => setTimeout(r, 200));
    await worker.stop();

    expect(metrics.getCounter("jobs_dead_lettered_total")).toBe(1);
  });

  test("times out long running job", async () => {
    const processor = {
      process: jest.fn().mockImplementation(
        () => new Promise((r) => setTimeout(r, 2000))
      ),
    };

    const worker = new Worker(
      queue,
      processor,
      new ExponentialBackoffRetryPolicy(1, 10),
      idempotency,
      logger,
      metrics,
      clock,
      { concurrency: 1, pollIntervalMs: 10, jobTimeoutMs: 50 }
    );

    const job = new Job("test");
    await queue.enqueue(job);

    await worker.start();
    await new Promise((r) => setTimeout(r, 200));
    await worker.stop();

    expect(metrics.getCounter("jobs_failed_total")).toBeGreaterThan(0);
  });
});
