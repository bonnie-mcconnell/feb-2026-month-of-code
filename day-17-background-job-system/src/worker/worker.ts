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
  ) {}

  async start(): Promise<void> {
    if (this.running) return;
    this.running = true;
    void this.runLoop();
  }

  async stop(): Promise<void> {
    this.running = false;
    while (this.activeJobs > 0) {
      await this.clock.sleep(10);
    }
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

      void this.processJob(job);
    }
  }

  private async processJob(job: Job): Promise<void> {
    this.activeJobs++;

    try {
      await this.handle(job);
    } finally {
      this.activeJobs--;
    }
  }

  private async handle(job: Job): Promise<void> {
    if (job.idempotencyKey) {
      const processed = await this.idempotencyStore.has(job.idempotencyKey);
      if (processed) {
        this.metrics.increment("jobs_skipped_idempotent");
        await this.queue.markCompleted(job.id);
        return;
      }
    }

    job.attempts++;

    try {
      await this.executeWithTimeout(job);

      if (job.idempotencyKey) {
        await this.idempotencyStore.markProcessed(job.idempotencyKey);
      }

      this.metrics.increment("jobs_completed_total");
      await this.queue.markCompleted(job.id);

    } catch (err) {
      await this.handleFailure(job, err as Error);
    }
  }

  private async handleFailure(job: Job, error: Error): Promise<void> {
    this.metrics.increment("jobs_failed_total");

    if (this.retryPolicy.shouldRetry(job.attempts, error)) {
      this.metrics.increment("jobs_retried_total");

      const delay = this.retryPolicy.nextDelay(job.attempts);
      await this.clock.sleep(delay);

      await this.queue.enqueue(job);
      return;
    }

    this.metrics.increment("jobs_dead_lettered_total");
    await this.queue.moveToDeadLetter(job.id);
  }

  private async executeWithTimeout(job: Job): Promise<void> {
    const timeout = (async () => {
      await this.clock.sleep(this.config.jobTimeoutMs);
      throw new Error("Job timed out");
    })();

    await Promise.race([
      this.processor.process(job),
      timeout
    ]);
  }
}
