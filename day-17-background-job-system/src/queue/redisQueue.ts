import { JobQueue } from "./queue";
import { Job } from "../domain/job";
import Redis from "ioredis";

export class RedisQueue implements JobQueue {
  private readonly pendingKey = "jobs:pending";
  private readonly processingKey = "jobs:processing";
  private readonly dlqKey = "jobs:dlq";
  private readonly jobPrefix = "jobs:data:";

  constructor(private readonly redis: Redis) {}

  async enqueue(job: Job): Promise<void> {
    const jobKey = `${this.jobPrefix}${job.id}`;
    await this.redis.multi()
      .hmset(jobKey, {
        id: job.id,
        name: job.name,
        payload: JSON.stringify(job.payload ?? {}),
        idempotencyKey: job.idempotencyKey ?? "",
        attempts: job.attempts.toString(),
      })
      .lpush(this.pendingKey, job.id)
      .exec();
  }

  async dequeue(): Promise<Job | null> {
    const jobId = await this.redis.rpoplpush(
      this.pendingKey,
      this.processingKey
    );
    if (!jobId) return null;

    const job = await this.getJob(jobId);
    return job ?? null;
  }

  async getJob(jobId: string): Promise<Job | undefined> {
    const data = await this.redis.hgetall(`${this.jobPrefix}${jobId}`);
    if (!data.id) return undefined;

    const job = new Job(
      data.name,
      JSON.parse(data.payload ?? "{}"),
      data.idempotencyKey || undefined
    );
    job.attempts = Number(data.attempts ?? 0);
    return job;
  }

  async markCompleted(jobId: string): Promise<void> {
    await this.redis.multi()
      .lrem(this.processingKey, 0, jobId)
      .del(`${this.jobPrefix}${jobId}`)
      .exec();
  }

  async markFailed(jobId: string): Promise<void> {
    await this.redis.lrem(this.processingKey, 0, jobId);
  }

  async moveToDeadLetter(jobId: string): Promise<void> {
    await this.redis.multi()
      .lrem(this.processingKey, 0, jobId)
      .lpush(this.dlqKey, jobId)
      .exec();
  }

  async getDeadLetterJobs(): Promise<Job[]> {
    const ids = await this.redis.lrange(this.dlqKey, 0, -1);
    const jobs: Job[] = [];
    for (const id of ids) {
      const job = await this.getJob(id);
      if (job) jobs.push(job);
    }
    return jobs;
  }
}
