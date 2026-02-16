import { JobQueue } from "../queue/queue";
import { RetryPolicy } from "../domain/retryPolicy";
import { JobProcessor } from "../domain/jobProcessor";
import { IdempotencyStore } from "../idempotency/idempotencyStore";
import { Logger } from "../infrastructure/logger";
import { Metrics } from "../infrastructure/metrics";
import { Clock } from "../infrastructure/clock";
import { Job } from "../domain/job";

export interface WorkerConfig {
  concurrency: number;
  pollIntervalMs: number;
  jobTimeoutMs: number;
}

export class Worker {
  private running = false;
  private activeJobs = 0;

  constructor(
    private readonly queue: JobQueue,
    private readonly processor: JobProcessor,
    private readonly retryPolicy: RetryPolicy,
    private readonly idempotencyStore: IdempotencyStore,
    private readonly logger: Logger,
    private readonly metrics: Metrics,
    private readonly clock: Clock,
    private readonly config: WorkerConfig
  ) {
    if (config.concurrency <= 0) {
      throw new Error("concurrency must be > 0");
    }

    if (config.pollIntervalMs <= 0) {
      throw new Error("pollIntervalMs must be > 0");
    }

    if (config.jobTimeoutMs <= 0) {
      throw new Error("jobTimeoutMs must be > 0");
    }
  }

  async start(): Promise<void> {
    if (this.running) return;

    this.running = true;

    this.logger.log({
      level: "info",
      event: "worker_started",
      timestamp: this.clock.now(),
    });

    void this.runLoop();
  }

  async stop(): Promise<void> {
    if (!this.running) return;

    this.running = false;

    this.logger.log({
      level: "info",
      event: "worker_stopping",
      timestamp: this.clock.now(),
    });

    while (this.activeJobs > 0) {
      await this.clock.sleep(10);
    }

    this.logger.log({
      level: "info",
      event: "worker_stopped",
      timestamp: this.clock.now(),
    });
  }

  private async runLoop(): Promise<void> {
    while (this.running) {
      if (this.activeJobs >= this.config.concurrency) {
        await this.clock.sleep(this.config.pollIntervalMs);
        continue;
      }

      const job = await this.queue.dequeue();

      if (!job) {
        await this.clock.sleep(this.config.pollIntervalMs);
        continue;
      }

      this.processJobSafely(job).catch((err) => {
        this.logger.log({
          level: "error",
          event: "worker_unhandled_error",
          timestamp: this.clock.now(),
          error: {
            name: err.name,
            message: err.message,
            stack: err.stack,
          },
        });
      });
    }
  }

  private async processJobSafely(job: Job): Promise<void> {
    this.activeJobs++;

    try {
      await this.handleJob(job);
    } finally {
      this.activeJobs--;
    }
  }

  private async handleJob(job: Job): Promise<void> {
    const startTime = this.clock.now();

    this.logger.log({
      level: "info",
      event: "job_started",
      timestamp: startTime,
      jobId: job.id,
      attempt: job.attempts + 1,
    });

    if (job.idempotencyKey) {
      const alreadyProcessed = await this.idempotencyStore.has(
        job.idempotencyKey
      );

      if (alreadyProcessed) {
        await this.queue.markCompleted(job.id);

        this.logger.log({
          level: "info",
          event: "job_skipped_idempotent",
          timestamp: this.clock.now(),
          jobId: job.id,
        });

        this.metrics.increment("jobs_skipped_idempotent");

        return;
      }
    }

    job.attempts += 1;
    job.lastAttemptAt = this.clock.now();

    try {
      await this.executeWithTimeout(job);

      await this.queue.markCompleted(job.id);

      if (job.idempotencyKey) {
        await this.idempotencyStore.markProcessed(job.idempotencyKey);
      }

      const duration = this.clock.now() - startTime;

      this.metrics.increment("jobs_completed_total");
      this.metrics.observe("job_duration_ms", duration);

      this.logger.log({
        level: "info",
        event: "job_completed",
        timestamp: this.clock.now(),
        jobId: job.id,
        attempt: job.attempts,
        metadata: { duration },
      });
    } catch (err) {
      await this.handleFailure(job, err as Error);
    }
  }

  private async handleFailure(job: Job, err: Error): Promise<void> {
    this.metrics.increment("jobs_failed_total");

    this.logger.log({
      level: "warn",
      event: "job_failed",
      timestamp: this.clock.now(),
      jobId: job.id,
      attempt: job.attempts,
      error: {
        name: err.name,
        message: err.message,
        stack: err.stack,
      },
    });

    const decision = this.retryPolicy.evaluate(job);

    if (decision.shouldRetry && decision.delayMs !== undefined) {
      this.metrics.increment("jobs_retried_total");

      this.logger.log({
        level: "info",
        event: "job_retried",
        timestamp: this.clock.now(),
        jobId: job.id,
        attempt: job.attempts,
        metadata: { delayMs: decision.delayMs },
      });

      await this.queue.markFailed(job.id);

      await this.clock.sleep(decision.delayMs);

      job.status = "pending";
      await this.queue.enqueue(job);

      return;
    }

    if (decision.shouldDeadLetter) {
      await this.queue.moveToDeadLetter(job.id);

      this.metrics.increment("jobs_dead_lettered_total");

      this.logger.log({
        level: "error",
        event: "job_dead_lettered",
        timestamp: this.clock.now(),
        jobId: job.id,
        attempt: job.attempts,
      });
    }
  }

  private async executeWithTimeout(job: Job): Promise<void> {
    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error("Job timed out")), this.config.jobTimeoutMs)
    );

    await Promise.race([
      this.processor.process(job),
      timeoutPromise,
    ]);
  }
}
