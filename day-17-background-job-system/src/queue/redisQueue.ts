import { JobQueue } from "./queue";
import { Job } from "../domain/job";
import Redis from "ioredis";

export class RedisQueue implements JobQueue {
  private readonly JOB_LIST = "jobs";
  private readonly DEAD_LETTER_SET = "dead_letter_jobs";

  constructor(private readonly redis: Redis) {}

  async enqueue(job: Job): Promise<void> {
    await this.redis.lpush(this.JOB_LIST, JSON.stringify(job));
  }

  async dequeue(): Promise<Job | null> {
    const raw = await this.redis.rpop(this.JOB_LIST);
    if (!raw) return null;

    const parsed = JSON.parse(raw);

    const job = new Job(
      parsed.name,
      parsed.payload,
      parsed.idempotencyKey
    );

    job.attempts = parsed.attempts ?? 0;

    return job;
  }

  async markCompleted(_jobId: string): Promise<void> {
    // no-op (job removed from queue on dequeue)
  }

  async markFailed(_jobId: string): Promise<void> {
    // no-op
  }

  async moveToDeadLetter(jobId: string): Promise<void> {
    const job = await this.getJob(jobId);
    if (!job) return;

    await this.redis.sadd(this.DEAD_LETTER_SET, JSON.stringify(job));
  }

  async getDeadLetterJobs(): Promise<Job[]> {
    const raw = await this.redis.smembers(this.DEAD_LETTER_SET);

    return raw.map(j => {
      const parsed = JSON.parse(j);
      const job = new Job(
        parsed.name,
        parsed.payload,
        parsed.idempotencyKey
      );
      job.attempts = parsed.attempts ?? 0;
      return job;
    });
  }

  async getJob(_jobId: string): Promise<Job | undefined> {
    // Redis list doesn't allow direct lookup by ID.
    // For production you'd use a separate hash store.
    return undefined;
  }
}
