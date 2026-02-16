import { Job } from "../domain/job";
import { JobQueue } from "./queue";

export class InMemoryQueue implements JobQueue {
  private readonly jobs = new Map<string, Job>();
  private readonly pendingOrder: string[] = [];

  async enqueue(job: Job): Promise<void> {
    if (this.jobs.has(job.id)) {
      throw new Error(`Job with id ${job.id} already exists`);
    }

    this.jobs.set(job.id, job);
    this.pendingOrder.push(job.id);
  }

  async dequeue(): Promise<Job | null> {
    while (this.pendingOrder.length > 0) {
      const jobId = this.pendingOrder.shift();
      if (!jobId) continue;

      const job = this.jobs.get(jobId);
      if (!job) continue;

      if (job.status !== "pending") {
        continue;
      }

      job.status = "processing";
      return job;
    }

    return null;
  }

  async markCompleted(jobId: string): Promise<void> {
    const job = this.jobs.get(jobId);
    if (!job) {
      throw new Error(`Job ${jobId} not found`);
    }

    job.status = "completed";
  }

  async markFailed(jobId: string): Promise<void> {
    const job = this.jobs.get(jobId);
    if (!job) {
      throw new Error(`Job ${jobId} not found`);
    }

    job.status = "failed";
  }

  async moveToDeadLetter(jobId: string): Promise<void> {
    const job = this.jobs.get(jobId);
    if (!job) {
      throw new Error(`Job ${jobId} not found`);
    }

    job.status = "dead_lettered";
  }

  async getJob(jobId: string): Promise<Job | undefined> {
    return this.jobs.get(jobId);
  }
}
